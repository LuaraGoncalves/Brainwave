from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.document import Dataset
from app.models.usuario import Usuario
from app.services.embedding_service import create_text_embedding

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/data-dictionary")
def data_dictionary(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    datasets = db.query(Dataset).order_by(Dataset.name.asc()).all()
    return [
        {
            "dataset": dataset.name,
            "table": dataset.table_name,
            "description": dataset.description,
            "columns": dataset.columns,
        }
        for dataset in datasets
    ]


@router.get("/system-map")
def system_map(current_user: Usuario = Depends(get_current_user)):
    modules = [
        "auth",
        "chat",
        "analytics",
        "datasets",
        "alerts",
        "reports",
        "query",
        "documents",
    ]
    return {
        "name": "Brainwave BI Assistant",
        "modules": modules,
        "flow": [
            "usuario pergunta em portugues",
            "backend escolhe SQL seguro",
            "consulta roda em modo leitura",
            "API retorna resposta, tabela, grafico e insights",
        ],
    }


@router.post("/embedding-preview")
def embedding_preview(
    payload: dict[str, str],
    current_user: Usuario = Depends(get_current_user),
):
    text = payload.get("text", "")
    return {"text": text, "embedding": create_text_embedding(text)}
