from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.services.chatbot_service import execute_safe_query

router = APIRouter(prefix="/query", tags=["query"])


class SqlRequest(BaseModel):
    sql: str


@router.post("/sql")
def run_sql(
    payload: SqlRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        columns, rows = execute_safe_query(db, payload.sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"columns": columns, "rows": rows}
