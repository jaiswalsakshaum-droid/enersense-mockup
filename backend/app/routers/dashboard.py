from fastapi import APIRouter
from app.models.dashboard import DashboardSummary
from app.data.dashboard import DASHBOARD_DATA

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    """
    Retrieve overall energy health summary, KPIs, today's consumption/cost/CO2,
    active alerts, peer benchmark comparators, and 24h plant load trends.
    """
    return DashboardSummary(**DASHBOARD_DATA)
