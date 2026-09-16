from pydantic import BaseModel, Field
from typing import List

class PeerBenchmark(BaseModel):
    plant_score: int
    peer_average_score: int
    peer_top_quartile: int
    industry_label: str
    percentile: int
    comparison_text: str

class DashboardAlertPreview(BaseModel):
    id: int
    machine_name: str
    detail: str
    time: str
    severity: str

class DashboardSummary(BaseModel):
    plant_name: str
    health_score: int
    score_target: int
    health_change_pct: float
    energy_use_today_kwh: float
    energy_use_change_pct: float
    energy_cost_today_inr: float
    energy_cost_change_pct: float
    co2e_today_tons: float
    co2e_change_pct: float
    active_alerts_count: int
    active_alerts_change: str
    energy_trend_24h: List[float] = Field(default_factory=list)
    baseline_trend_24h: List[float] = Field(default_factory=list)
    peer_benchmark: PeerBenchmark
    latest_alerts: List[DashboardAlertPreview] = Field(default_factory=list)
