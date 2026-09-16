from pydantic import BaseModel
from typing import Literal, Optional

AlertSeverity = Literal["Critical", "Warning", "Resolved", "Info"]

class AlertItem(BaseModel):
    id: int
    title: str
    detail: str
    time: str
    severity: AlertSeverity
    machine: str
    machine_id: Optional[str] = None
    timestamp: Optional[str] = None
    recommended_action: Optional[str] = None
