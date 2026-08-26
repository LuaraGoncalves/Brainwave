from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


FORBIDDEN_SQL = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
)


@dataclass
class AnalysisPlan:
    sql: str
    answer_template: str
    chart_type: str
    chart_title: str


def is_safe_select(sql: str) -> bool:
    cleaned = sql.strip().lower()
    if not cleaned.startswith("select"):
        return False
    if ";" in cleaned[:-1]:
        return False
    return not any(word in cleaned for word in FORBIDDEN_SQL)


def build_analysis_plan(question: str) -> AnalysisPlan:
    normalized = question.lower()

    if "produto" in normalized and any(term in normalized for term in ["mais", "maior", "top"]):
        return AnalysisPlan(
            sql=(
                "SELECT product AS label, SUM(revenue) AS value "
                "FROM salerecord GROUP BY product ORDER BY value DESC LIMIT 5"
            ),
            answer_template="Os produtos com maior faturamento aparecem no ranking abaixo.",
            chart_type="bar",
            chart_title="Top produtos por faturamento",
        )

    if "regiao" in normalized or "região" in normalized:
        return AnalysisPlan(
            sql=(
                "SELECT region AS label, SUM(revenue) AS value "
                "FROM salerecord GROUP BY region ORDER BY value DESC"
            ),
            answer_template="A analise por regiao mostra onde a receita esta mais forte.",
            chart_type="bar",
            chart_title="Faturamento por regiao",
        )

    if "categoria" in normalized:
        return AnalysisPlan(
            sql=(
                "SELECT category AS label, SUM(revenue) AS value "
                "FROM salerecord GROUP BY category ORDER BY value DESC"
            ),
            answer_template="A analise por categoria mostra quais linhas puxam o resultado.",
            chart_type="bar",
            chart_title="Faturamento por categoria",
        )

    if "mes" in normalized or "mês" in normalized or "mensal" in normalized:
        return AnalysisPlan(
            sql=(
                "SELECT strftime('%Y-%m', order_date) AS label, SUM(revenue) AS value "
                "FROM salerecord GROUP BY label ORDER BY label"
            ),
            answer_template="A evolucao mensal mostra a receita ao longo do tempo.",
            chart_type="line",
            chart_title="Faturamento mensal",
        )

    if "ticket" in normalized or "media" in normalized or "média" in normalized:
        return AnalysisPlan(
            sql=(
                "SELECT category AS label, ROUND(AVG(revenue), 2) AS value "
                "FROM salerecord GROUP BY category ORDER BY value DESC"
            ),
            answer_template="O ticket medio por categoria ajuda a entender valor por pedido.",
            chart_type="bar",
            chart_title="Ticket medio por categoria",
        )

    return AnalysisPlan(
        sql=(
            "SELECT strftime('%Y-%m', order_date) AS label, SUM(revenue) AS value "
            "FROM salerecord GROUP BY label ORDER BY label"
        ),
        answer_template="Montei uma visao geral de faturamento para comecar a analise.",
        chart_type="line",
        chart_title="Visao geral de faturamento",
    )


def adapt_sql_for_database(sql: str, dialect_name: str) -> str:
    if dialect_name == "postgresql":
        return sql.replace("strftime('%Y-%m', order_date)", "to_char(order_date, 'YYYY-MM')")
    return sql


def execute_safe_query(db: Session, sql: str) -> tuple[list[str], list[dict[str, Any]]]:
    if not is_safe_select(sql):
        raise ValueError("Apenas consultas SELECT seguras sao permitidas.")

    final_sql = adapt_sql_for_database(sql, db.bind.dialect.name)
    result = db.execute(text(final_sql))
    columns = list(result.keys())
    rows = [dict(row._mapping) for row in result.fetchall()]
    return columns, rows


def build_chart(rows: list[dict[str, Any]], chart_type: str, title: str) -> dict[str, Any] | None:
    if not rows or "label" not in rows[0] or "value" not in rows[0]:
        return None
    return {
        "type": chart_type,
        "title": title,
        "labels": [str(row["label"]) for row in rows],
        "values": [float(row["value"] or 0) for row in rows],
    }


def build_insights(rows: list[dict[str, Any]]) -> list[str]:
    if not rows or "label" not in rows[0] or "value" not in rows[0]:
        return ["A consulta retornou dados, mas sem colunas padronizadas para insight automatico."]

    values = [float(row["value"] or 0) for row in rows]
    total = sum(values)
    top = max(rows, key=lambda row: float(row["value"] or 0))
    insights = [f"{top['label']} lidera com {float(top['value']):,.2f}."]
    if total:
        share = float(top["value"] or 0) / total * 100
        insights.append(f"O lider representa {share:.1f}% do total analisado.")
    if len(values) > 1:
        insights.append(f"Foram encontrados {len(values)} grupos comparaveis nessa analise.")
    return insights


def analyze_question(db: Session, question: str) -> dict[str, Any]:
    plan = build_analysis_plan(question)
    columns, rows = execute_safe_query(db, plan.sql)
    chart = build_chart(rows, plan.chart_type, plan.chart_title)
    return {
        "question": question,
        "answer": plan.answer_template,
        "sql": adapt_sql_for_database(plan.sql, db.bind.dialect.name),
        "columns": columns,
        "rows": rows,
        "chart": chart,
        "insights": build_insights(rows),
    }
