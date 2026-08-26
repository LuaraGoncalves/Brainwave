from datetime import datetime
from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    chat_id: int | None = None


class ChartPayload(BaseModel):
    type: str
    title: str
    labels: list[str]
    values: list[float]


class QueryResponse(BaseModel):
    chat_id: int
    question: str
    answer: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    chart: ChartPayload | None = None
    insights: list[str]


class ChatSummary(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}
