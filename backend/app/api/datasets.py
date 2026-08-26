import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.document import Dataset, SaleRecord
from app.models.usuario import Usuario

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
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    required = {"order_date", "region", "category", "product", "quantity", "unit_price"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=400,
            detail="CSV precisa ter order_date, region, category, product, quantity e unit_price",
        )

    records = []
    for row in reader:
        quantity = int(row["quantity"])
        unit_price = int(row["unit_price"])
        records.append(
            SaleRecord(
                order_date=datetime.fromisoformat(row["order_date"]),
                region=row["region"],
                category=row["category"],
                product=row["product"],
                quantity=quantity,
                unit_price=unit_price,
                revenue=quantity * unit_price,
            )
        )

    db.add_all(records)
    if db.query(Dataset).filter(Dataset.name == file.filename).first() is None:
        db.add(
            Dataset(
                name=file.filename or "CSV importado",
                source="upload",
                table_name="salerecord",
                description="Dados importados por CSV pelo usuario.",
                columns=list(required) + ["revenue"],
            )
        )
    db.commit()
    return {"imported_rows": len(records)}


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
