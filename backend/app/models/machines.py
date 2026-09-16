from pydantic import BaseModel, Field
from typing import List, Optional, Literal

MachineStatus = Literal["Normal", "Warning", "Critical"]

class MachineReading(BaseModel):
    timestamp: str
    power_kw: float
    temperature_c: float
    vibration_mms: float

class MaintenanceRecord(BaseModel):
    date: str
    title: str
    detail: str
    active: bool = False

class Machine(BaseModel):
    id: str
    name: str
    type: str
    line: str
    score: int
    status: MachineStatus
    maintenance: str
    reading: str
    power_kw: float
    temperature_c: float
    vibration_mms: float

class MachineDetail(Machine):
    baseline_power_kw: float
    peak_power_kw: float
    avg_24h_power_kw: float
    recent_readings: List[MachineReading] = Field(default_factory=list)
    history_readings_24h: List[float] = Field(default_factory=list)
    maintenance_history: List[MaintenanceRecord] = Field(default_factory=list)
