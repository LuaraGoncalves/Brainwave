from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.analytics import InsightAlert
from app.models.usuario import Usuario
from app.schemas.alert import AlertCreate, AlertRead, AlertStatusUpdate
from app.services.analytics_service import refresh_alert_values

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    refresh_alert_values(db)
    return db.query(InsightAlert).order_by(InsightAlert.created_at.desc()).all()


@router.post("", response_model=AlertRead)
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if payload.metric not in {"revenue", "orders"}:
        raise HTTPException(status_code=400, detail="Metricas permitidas: revenue ou orders")
    if payload.operator not in {">", "<"}:
        raise HTTPException(status_code=400, detail="Operadores permitidos: > ou <")

    alert = InsightAlert(**payload.model_dump())
    db.add(alert)
    db.commit()
    refresh_alert_values(db)
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/status", response_model=AlertRead)
def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    alert = db.query(InsightAlert).filter(InsightAlert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta nao encontrado")
    if payload.status not in {"open", "watching", "resolved"}:
        raise HTTPException(status_code=400, detail="Status invalido")
    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    alert = db.query(InsightAlert).filter(InsightAlert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta nao encontrado")
    db.delete(alert)
    db.commit()
    return {"deleted": True}
