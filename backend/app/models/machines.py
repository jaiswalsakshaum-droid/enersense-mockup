from pydantic import BaseModel, Field
from typing import List, Optional, Literal

MachineStatus = Literal["Normal", "Warning", "Critical"]

class MachineReading(BaseModel):
    timestamp: str
    power_kw: float
    temperature_c: float
    vibration_mms: float


class PowerHealthFactor(BaseModel):
    value: float
    baseline: float
    deviation_pct: float
    status: str
    penalty: float


class VibrationHealthFactor(BaseModel):
    value: float
    status: str
    penalty: float

class TemperatureHealthFactor(BaseModel):
    value: float
    expected: float
    deviation: float
    status: str
    penalty: float
    
class HealthFactors(BaseModel):
    power: PowerHealthFactor
    vibration: VibrationHealthFactor
    temperature: TemperatureHealthFactor

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
    health_factors: HealthFactors
    recent_readings: List[MachineReading] = Field(default_factory=list)
    history_readings_24h: List[float] = Field(default_factory=list)
    maintenance_history: List[MaintenanceRecord] = Field(default_factory=list)
