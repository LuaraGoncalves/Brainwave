from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.analytics import DataConnection, InsightAlert
from app.models.document import SaleRecord
from app.models.usuario import Usuario
from app.services.dataset_service import import_sales_csv_file

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

    csv_path = Path(__file__).resolve().parents[1] / "data" / "sales.csv"
    imported_rows = import_sales_csv_file(db, csv_path, dataset_name="Vendas CSV 2026", source="csv")
    logger.info(f"Dataset de vendas criado com {imported_rows} linhas do CSV.")


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
