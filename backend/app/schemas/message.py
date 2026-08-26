from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    sql: str | None = None
    result: dict[str, Any] | list[dict[str, Any]] | None = None
    chart: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
