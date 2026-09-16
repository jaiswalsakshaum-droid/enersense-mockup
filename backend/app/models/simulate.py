from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

InterventionType = Literal["load_shift", "equipment_upgrade", "process_change"]

class SimulateRequest(BaseModel):
    intervention_type: InterventionType
    params: Dict[str, Any] = Field(default_factory=dict)

class SimulateResponse(BaseModel):
    intervention_type: InterventionType
    intervention_title: str
    baseline_kwh: float
    projected_kwh: float
    kwh_saved_monthly: float
    percent_reduction: float
    baseline_cost_rupees_per_month: float
    projected_cost_rupees_per_month: float
    projected_savings_rupees_per_month: float
    estimated_capex_rupees: float
    payback_months: float
    co2_reduction_tons_per_year: float
    summary: str
    breakdown: Dict[str, Any] = Field(default_factory=dict)
