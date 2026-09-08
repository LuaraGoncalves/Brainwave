import io

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.document import Dataset, SaleRecord
from app.models.usuario import Usuario
from app.services.dataset_service import import_sales_csv

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def list_datasets(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "source": item.source,
            "table_name": item.table_name,
            "description": item.description,
            "columns": item.columns,
            "created_at": item.created_at,
        }
        for item in datasets
    ]


@router.get("/sales/sample")
def sales_sample(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    rows = db.query(SaleRecord).order_by(SaleRecord.order_date.desc()).limit(min(limit, 50)).all()
    return [
        {
            "order_date": row.order_date.date().isoformat(),
            "region": row.region,
            "category": row.category,
            "product": row.product,
            "quantity": row.quantity,
            "unit_price": row.unit_price,
            "revenue": row.revenue,
        }
        for row in rows
    ]


@router.post("/sales/upload")
def upload_sales_csv(
    replace: bool = True,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    content = file.file.read().decode("utf-8-sig")
    imported_rows = import_sales_csv(
        db,
        content,
        dataset_name=file.filename or "CSV importado",
        source="upload",
        replace=replace,
    )
    return {"imported_rows": imported_rows, "replace": replace}


@router.get("/sales/export")
def export_sales_csv(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["order_date", "region", "category", "product", "quantity", "unit_price", "revenue"])
    rows = db.query(SaleRecord).order_by(SaleRecord.order_date.asc()).all()
    for row in rows:
        writer.writerow([
            row.order_date.date().isoformat(),
            row.region,
            row.category,
            row.product,
            row.quantity,
            row.unit_price,
            row.revenue,
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=brainwave-sales.csv"},
    )
