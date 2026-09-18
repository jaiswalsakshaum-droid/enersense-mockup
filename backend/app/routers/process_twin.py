from fastapi import APIRouter, HTTPException
from app.services.process_simulation import simulate_order

router = APIRouter(
    prefix="/api/process-twin",
    tags=["ProcessTwin"]
)


@router.post("/simulate/{order_id}")
def run_process_twin(order_id: str):

    result = simulate_order(order_id)

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result
