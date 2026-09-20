from fastapi import APIRouter
from typing import List

from app.models.alerts import AlertItem
from app.data.alerts import ALERTS_DATA
from app.services.alert_engine import get_alert_history


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get("", response_model=List[AlertItem])
async def get_alerts():
    """
    Retrieve historical and simulated machine-condition alerts.
    """

    historical_alerts = [
        AlertItem(**alert)
        for alert in ALERTS_DATA
    ]

    dynamic_alerts = [
        AlertItem(**alert)
        for alert in get_alert_history()
    ]

    return dynamic_alerts + historical_alerts