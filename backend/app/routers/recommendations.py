from fastapi import APIRouter
from typing import List
from app.models.recommendations import RecommendationItem
from app.data.recommendations import RECOMMENDATIONS_DATA

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=List[RecommendationItem])
async def get_recommendations():
    """
    Retrieve ranked energy audit recommendations with savings estimates, rupee impact, and payback periods.
    """
    return [RecommendationItem(**rec) for rec in RECOMMENDATIONS_DATA]
