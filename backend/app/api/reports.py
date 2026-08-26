import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.analytics import Report
from app.models.usuario import Usuario
from app.schemas.report import ReportCreate, ReportRead
from app.services.analytics_service import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return generate_report(db, current_user, payload.title, payload.period)


@router.get("", response_model=list[ReportRead])
def list_reports(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )


@router.get("/{report_id}", response_model=ReportRead)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Relatorio nao encontrado")
    return report


@router.get("/{report_id}/export")
def export_report_csv(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Relatorio nao encontrado")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["section", "label", "value"])
    for metric in report.payload.get("metrics", []):
        writer.writerow(["metric", metric["label"], metric["value"]])
    for section in ["monthly_revenue", "revenue_by_region", "revenue_by_category", "top_products"]:
        for point in report.payload.get(section, []):
            writer.writerow([section, point["label"], point["value"]])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=brainwave-report-{report.id}.csv"},
    )
