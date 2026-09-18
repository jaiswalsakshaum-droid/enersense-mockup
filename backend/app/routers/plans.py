from fastapi import APIRouter, HTTPException

from app.services.optimization_service import optimize_order
from app.services.plan_service import save_optimized_plan

router = APIRouter(
    prefix="/api/plans",
    tags=["Production Plans"]
)


@router.post("/generate/{order_id}")
def generate_plan(order_id: str):

    # Run optimizer
    result = optimize_order(order_id)

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    best_plan = result.get("best_plan")

    if not best_plan:
        raise HTTPException(
            status_code=400,
            detail="No feasible production plan found"
        )

    # Save winning plan
    saved_plan = save_optimized_plan(
        order_id,
        best_plan
    )

    return {
        "message": "Production plan generated successfully",
        "optimization": result,
        "saved_plan": saved_plan
    }