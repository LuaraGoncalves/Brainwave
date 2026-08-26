from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analytics import InsightAlert, Report, SavedAnalysis
from app.models.document import SaleRecord
from app.models.usuario import Usuario
from app.schemas.analytics import SavedAnalysisCreate


def money(value: int | float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def get_total_revenue(db: Session) -> int:
    return int(db.query(func.coalesce(func.sum(SaleRecord.revenue), 0)).scalar() or 0)


def get_total_orders(db: Session) -> int:
    return int(db.query(func.count(SaleRecord.id)).scalar() or 0)


def _rows_to_points(rows: list[tuple[Any, Any]]) -> list[dict[str, Any]]:
    return [{"label": str(label), "value": float(value or 0)} for label, value in rows]


def get_month_expression(db: Session):
    if db.bind.dialect.name == "postgresql":
        return func.to_char(SaleRecord.order_date, "YYYY-MM")
    return func.strftime("%Y-%m", SaleRecord.order_date)


def get_overview(db: Session) -> dict[str, Any]:
    total_revenue = get_total_revenue(db)
    total_orders = get_total_orders(db)
    average_ticket = int(total_revenue / total_orders) if total_orders else 0

    month_expr = get_month_expression(db).label("label")
    monthly = (
        db.query(month_expr, func.sum(SaleRecord.revenue))
        .group_by(month_expr)
        .order_by(month_expr)
        .all()
    )
    by_region = (
        db.query(SaleRecord.region, func.sum(SaleRecord.revenue))
        .group_by(SaleRecord.region)
        .order_by(func.sum(SaleRecord.revenue).desc())
        .all()
    )
    by_category = (
        db.query(SaleRecord.category, func.sum(SaleRecord.revenue))
        .group_by(SaleRecord.category)
        .order_by(func.sum(SaleRecord.revenue).desc())
        .all()
    )
    top_products = (
        db.query(SaleRecord.product, func.sum(SaleRecord.revenue))
        .group_by(SaleRecord.product)
        .order_by(func.sum(SaleRecord.revenue).desc())
        .limit(5)
        .all()
    )

    leader_region = by_region[0][0] if by_region else "--"
    leader_product = top_products[0][0] if top_products else "--"

    return {
        "metrics": [
            {"label": "Receita total", "value": money(total_revenue), "helper": "Soma do dataset de vendas"},
            {"label": "Pedidos", "value": total_orders, "helper": "Registros analisados"},
            {"label": "Ticket medio", "value": money(average_ticket), "helper": "Receita dividida por pedido"},
            {"label": "Regiao lider", "value": leader_region, "helper": f"Produto lider: {leader_product}"},
        ],
        "monthly_revenue": _rows_to_points(monthly),
        "revenue_by_region": _rows_to_points(by_region),
        "revenue_by_category": _rows_to_points(by_category),
        "top_products": _rows_to_points(top_products),
    }


def save_analysis(db: Session, user: Usuario, payload: SavedAnalysisCreate) -> SavedAnalysis:
    analysis = SavedAnalysis(
        user_id=user.id,
        title=payload.title,
        question=payload.question,
        sql=payload.sql,
        chart=payload.chart,
        insights=payload.insights,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def list_saved_analyses(db: Session, user: Usuario) -> list[SavedAnalysis]:
    return (
        db.query(SavedAnalysis)
        .filter(SavedAnalysis.user_id == user.id)
        .order_by(SavedAnalysis.created_at.desc())
        .all()
    )


def refresh_alert_values(db: Session) -> None:
    total_revenue = get_total_revenue(db)
    total_orders = get_total_orders(db)
    values = {"revenue": total_revenue, "orders": total_orders}

    alerts = db.query(InsightAlert).all()
    for alert in alerts:
        current = values.get(alert.metric, 0)
        alert.current_value = current
        if alert.operator == ">" and current > alert.threshold:
            alert.status = "open"
        elif alert.operator == "<" and current < alert.threshold:
            alert.status = "open"
        elif alert.status != "resolved":
            alert.status = "watching"
    db.commit()


def generate_report(db: Session, user: Usuario, title: str, period: str) -> Report:
    overview = get_overview(db)
    top_product = overview["top_products"][0]["label"] if overview["top_products"] else "sem dados"
    summary = (
        f"No periodo {period}, a receita total foi {overview['metrics'][0]['value']}. "
        f"O produto com melhor desempenho foi {top_product}."
    )
    report = Report(
        user_id=user.id,
        title=title,
        period=period,
        summary=summary,
        payload=overview,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
