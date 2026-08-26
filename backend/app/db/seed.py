from datetime import datetime

from loguru import logger
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.analytics import DataConnection, InsightAlert
from app.models.document import Dataset, SaleRecord
from app.models.usuario import Usuario

def seed_usuarios(db: Session):
    if db.query(Usuario).first() is None:
        logger.info("Criando usuários default (seeds)...")
        admin = Usuario(
            email="admin@brainwave.bi",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        analyst = Usuario(
            email="analyst@brainwave.bi",
            hashed_password=get_password_hash("analyst123"),
            is_active=True
        )
        db.add_all([admin, analyst])
        db.commit()
        logger.info("Usuários criados com sucesso.")
    else:
        logger.info("A tabela de usuários já possui dados. Pulando seed.")


def seed_sales_dataset(db: Session):
    if db.query(SaleRecord).first() is not None:
        logger.info("Dataset de vendas ja possui dados. Pulando seed.")
        return

    logger.info("Criando dataset de vendas para analise BI...")
    rows = [
        ("2026-01-05", "Sudeste", "Software", "Assinatura Pro", 12, 390),
        ("2026-01-11", "Sul", "Servicos", "Consultoria BI", 4, 1200),
        ("2026-01-19", "Nordeste", "Hardware", "Sensor IoT", 18, 210),
        ("2026-02-03", "Sudeste", "Software", "Assinatura Pro", 15, 390),
        ("2026-02-14", "Centro-Oeste", "Software", "Dashboard Plus", 8, 540),
        ("2026-02-25", "Norte", "Servicos", "Treinamento", 5, 850),
        ("2026-03-02", "Sul", "Hardware", "Gateway Edge", 7, 980),
        ("2026-03-09", "Sudeste", "Servicos", "Consultoria BI", 6, 1200),
        ("2026-03-18", "Nordeste", "Software", "Dashboard Plus", 9, 540),
        ("2026-04-06", "Norte", "Hardware", "Sensor IoT", 21, 210),
        ("2026-04-12", "Centro-Oeste", "Servicos", "Treinamento", 7, 850),
        ("2026-04-21", "Sudeste", "Software", "Assinatura Pro", 20, 390),
        ("2026-05-04", "Sul", "Software", "Dashboard Plus", 13, 540),
        ("2026-05-16", "Nordeste", "Servicos", "Consultoria BI", 3, 1200),
        ("2026-05-26", "Sudeste", "Hardware", "Gateway Edge", 10, 980),
        ("2026-06-08", "Centro-Oeste", "Hardware", "Sensor IoT", 25, 210),
        ("2026-06-17", "Norte", "Software", "Assinatura Pro", 11, 390),
        ("2026-06-24", "Sul", "Servicos", "Consultoria BI", 5, 1200),
    ]
    records = [
        SaleRecord(
            order_date=datetime.fromisoformat(date),
            region=region,
            category=category,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            revenue=quantity * unit_price,
        )
        for date, region, category, product, quantity, unit_price in rows
    ]
    dataset = Dataset(
        name="Vendas 2026",
        source="seed",
        table_name="salerecord",
        description="Pedidos comerciais ficticios para demonstrar analise de dados.",
        columns=[
            "order_date",
            "region",
            "category",
            "product",
            "quantity",
            "unit_price",
            "revenue",
        ],
    )
    db.add(dataset)
    db.add_all(records)
    db.commit()
    logger.info("Dataset de vendas criado com sucesso.")


def seed_analytics_setup(db: Session):
    if db.query(DataConnection).first() is None:
        db.add(
            DataConnection(
                name="PostgreSQL BI Demo",
                engine="postgresql",
                host="db",
                database="brainwave_bi",
                status="active",
                is_read_only=True,
            )
        )

    if db.query(InsightAlert).first() is None:
        db.add_all(
            [
                InsightAlert(
                    title="Receita acima da meta",
                    metric="revenue",
                    operator=">",
                    threshold=80000,
                    severity="success",
                ),
                InsightAlert(
                    title="Poucos pedidos importados",
                    metric="orders",
                    operator="<",
                    threshold=10,
                    severity="warning",
                ),
            ]
        )
    db.commit()
    logger.info("Configuracoes de analytics criadas/verificadas.")

def main():
    logger.info("Iniciando injeção de dados (seeds)...")
    db = SessionLocal()
    try:
        seed_usuarios(db)
        seed_sales_dataset(db)
        seed_analytics_setup(db)
    except Exception as e:
        logger.error(f"Erro ao inserir seeds: {e}")
        db.rollback()
    finally:
        db.close()
    logger.info("Finalizado injeção de dados (seeds).")

if __name__ == "__main__":
    main()
