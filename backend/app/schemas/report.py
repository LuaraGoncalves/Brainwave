from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReportCreate(BaseModel):
    title: str
    period: str = "2026-H1"


class ReportRead(BaseModel):
    id: int
    user_id: int
    title: str
    period: str
    summary: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
