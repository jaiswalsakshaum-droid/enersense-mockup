from fastapi import APIRouter, HTTPException
from typing import List

from app.models.recommendations import RecommendationItem
from app.services.recommendation_engine import get_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get("", response_model=List[RecommendationItem])
async def get_recommendations_api():
    """
    Generate ranked energy-audit recommendations from
    PostgreSQL telemetry and energy tariffs.
    """

    try:
        recommendations = get_recommendations()

        return [
            RecommendationItem(**recommendation)
            for recommendation in recommendations
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {exc}",
        )