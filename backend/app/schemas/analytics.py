from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MetricCard(BaseModel):
    label: str
    value: str | int | float
    helper: str


class SeriesPoint(BaseModel):
    label: str
    value: float


class OverviewResponse(BaseModel):
    metrics: list[MetricCard]
    monthly_revenue: list[SeriesPoint]
    revenue_by_region: list[SeriesPoint]
    revenue_by_category: list[SeriesPoint]
    top_products: list[SeriesPoint]


class DataConnectionCreate(BaseModel):
    name: str
    engine: str = "postgresql"
    host: str = "localhost"
    database: str
    is_read_only: bool = True


class DataConnectionRead(DataConnectionCreate):
    id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SavedAnalysisCreate(BaseModel):
    title: str
    question: str
    sql: str
    chart: dict[str, Any] | None = None
    insights: list[str] = []


class SavedAnalysisRead(SavedAnalysisCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
