from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.analytics import DataConnection, SavedAnalysis
from app.models.usuario import Usuario
from app.schemas.analytics import (
    DataConnectionCreate,
    DataConnectionRead,
    OverviewResponse,
    SavedAnalysisCreate,
    SavedAnalysisRead,
)
from app.services.analytics_service import get_overview, list_saved_analyses, save_analysis

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewResponse)
def overview(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return get_overview(db)


@router.get("/connections", response_model=list[DataConnectionRead])
def list_connections(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return db.query(DataConnection).order_by(DataConnection.created_at.desc()).all()


@router.post("/connections", response_model=DataConnectionRead)
def create_connection(
    payload: DataConnectionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    existing = db.query(DataConnection).filter(DataConnection.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Conexao com esse nome ja existe")
    connection = DataConnection(**payload.model_dump(), status="active")
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@router.post("/saved", response_model=SavedAnalysisRead)
def create_saved_analysis(
    payload: SavedAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return save_analysis(db, current_user, payload)


@router.get("/saved", response_model=list[SavedAnalysisRead])
def saved_analyses(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return list_saved_analyses(db, current_user)


@router.delete("/saved/{analysis_id}")
def delete_saved_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    analysis = (
        db.query(SavedAnalysis)
        .filter(SavedAnalysis.id == analysis_id, SavedAnalysis.user_id == current_user.id)
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analise nao encontrada")
    db.delete(analysis)
    db.commit()
    return {"deleted": True}
