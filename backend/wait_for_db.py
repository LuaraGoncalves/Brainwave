import sys
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from sqlalchemy import text
from app.db.session import SessionLocal
from loguru import logger
import logging

max_tries = 60 * 5  # 5 minutos
wait_seconds = 1

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    try:
        db = SessionLocal()
        # Testa explicitamente se o banco aceita queries (não só conexões)
        db.execute(text("SELECT 1"))
        db.commit()
    except Exception as e:
        logger.error(f"PostgreSQL ainda não está aceitando comandos: {e}")
        raise e
    finally:
        db.close()

def main() -> None:
    logger.info("Inicializando conexão com banco de dados...")
    init()
    logger.info("PostgreSQL está ativo e responsivo!")

if __name__ == "__main__":
    main()