from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.schemes import SchemeItem
from app.data.schemes import SCHEMES_DATA

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=List[SchemeItem])
async def get_schemes(
    industry_type: Optional[str] = Query(None, description="Industry sector (e.g. foundry, textile, ceramics)"),
    monthly_consumption_kwh: Optional[float] = Query(None, description="Monthly consumption in kWh"),
):
    """
    Retrieve Indian government, BEE, SIDBI, and state energy efficiency schemes matching plant profile.
    """
    results = []
    for item in SCHEMES_DATA:
        if industry_type:
            ind_lower = industry_type.lower()
            if "all" not in item["eligible_industries"] and ind_lower not in [i.lower() for i in item["eligible_industries"]]:
                continue
        results.append(SchemeItem(**item))
    return results
