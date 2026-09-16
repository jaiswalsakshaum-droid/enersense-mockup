from pydantic import BaseModel

class RecommendationItem(BaseModel):
    rank: str
    title: str
    description: str
    saving: str
    rupees: str
    payback: str
    tag: str
    annual_saving_kwh: float
    monthly_saving_inr: float
    payback_months: float
    capex_inr: float
