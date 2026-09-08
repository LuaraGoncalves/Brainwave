import csv
import io
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Dataset, SaleRecord

SALES_COLUMNS = ["order_date", "region", "category", "product", "quantity", "unit_price", "revenue"]
REQUIRED_SALES_COLUMNS = {"order_date", "region", "category", "product", "quantity", "unit_price"}


def parse_sales_csv(content: str) -> list[SaleRecord]:
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not REQUIRED_SALES_COLUMNS.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=400,
            detail="CSV precisa ter order_date, region, category, product, quantity e unit_price",
        )

    records = []
    for row in reader:
        quantity = int(row["quantity"])
        unit_price = int(row["unit_price"])
        revenue = int(row.get("revenue") or quantity * unit_price)
        records.append(
            SaleRecord(
                order_date=datetime.fromisoformat(row["order_date"]),
                region=row["region"],
                category=row["category"],
                product=row["product"],
                quantity=quantity,
                unit_price=unit_price,
                revenue=revenue,
            )
        )
    return records


def import_sales_csv(db: Session, content: str, dataset_name: str, source: str, replace: bool = False) -> int:
    records = parse_sales_csv(content)
    if replace:
        db.query(SaleRecord).delete()

    db.add_all(records)
    dataset = db.query(Dataset).filter(Dataset.name == dataset_name).first()
    if dataset is None:
        dataset = Dataset(
            name=dataset_name,
            source=source,
            table_name="salerecord",
            description="Dados comerciais carregados a partir de arquivo CSV.",
            columns=SALES_COLUMNS,
        )
        db.add(dataset)
    else:
        dataset.source = source
        dataset.description = "Dados comerciais carregados a partir de arquivo CSV."
        dataset.columns = SALES_COLUMNS

    db.commit()
    return len(records)


def import_sales_csv_file(db: Session, path: Path, dataset_name: str, source: str = "csv") -> int:
    content = path.read_text(encoding="utf-8-sig")
    return import_sales_csv(db, content, dataset_name=dataset_name, source=source, replace=False)
