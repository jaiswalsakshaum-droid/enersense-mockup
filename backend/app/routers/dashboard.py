from fastapi import APIRouter, HTTPException

from app.models.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/summary",
    response_model=DashboardSummary
)
async def get_dashboard_summary_endpoint():

    try:
        return get_dashboard_summary()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )