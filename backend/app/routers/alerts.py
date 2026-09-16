from fastapi import APIRouter
from typing import List
from app.models.alerts import AlertItem
from app.data.alerts import ALERTS_DATA

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertItem])
async def get_alerts():
    """
    Retrieve operational alerts ordered by severity and timestamp.
    """
    return [AlertItem(**alert) for alert in ALERTS_DATA]
