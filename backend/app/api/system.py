from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "api_version": settings.API_V1_STR,
    }


@router.get("/readiness")
def readiness(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@router.get("/modules")
def modules():
    return {
        "modules": [
            {"name": "auth", "description": "Login, cadastro e token"},
            {"name": "chat", "description": "Perguntas em portugues com SQL seguro"},
            {"name": "analytics", "description": "Metricas, conexoes e analises salvas"},
            {"name": "datasets", "description": "Catalogo, upload, amostra e exportacao"},
            {"name": "alerts", "description": "Monitoramento de metas e indicadores"},
            {"name": "reports", "description": "Relatorios executivos e CSV"},
            {"name": "documents", "description": "Dicionario de dados e mapa do sistema"},
            {"name": "query", "description": "Execucao controlada de SELECT"},
        ]
    }
