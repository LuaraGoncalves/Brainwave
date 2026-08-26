from sqlalchemy import Column, DateTime, Integer, JSON, String, func

from app.db.base import Base


class Dataset(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False, default="seed")
    table_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    columns = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SaleRecord(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime(timezone=True), nullable=False)
    region = Column(String, nullable=False)
    category = Column(String, nullable=False)
    product = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    revenue = Column(Integer, nullable=False)
