from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime, timezone

Status = Literal["ON", "OFF"]

class CellLog(BaseModel):
    """
    A single ON/OFF event for a cell/tower at timestamp ts.
    """
    cell_id: int
    status: Status
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: int
    cluster: Optional[str] = None
