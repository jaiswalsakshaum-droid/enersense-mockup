from fastapi import APIRouter
from typing import List

from app.models.alerts import AlertItem
from app.services.alert_engine import get_alert_history

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertItem])
async def get_alerts():
    return [AlertItem(**alert) for alert in get_alert_history()]