from fastapi import APIRouter, HTTPException

from app.services.optimization_service import optimize_order


router = APIRouter(
    prefix="/api/optimization",
    tags=["Optimization"]
)


@router.post("/run/{order_id}")
def run_optimization(order_id: str):

    result = optimize_order(order_id)

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result