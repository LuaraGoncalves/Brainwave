from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    title: str
    metric: str
    operator: str
    threshold: int
    severity: str = "info"


class AlertRead(AlertCreate):
    id: int
    current_value: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertStatusUpdate(BaseModel):
    status: str
