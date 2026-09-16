from fastapi import APIRouter, HTTPException
from app.models.simulate import SimulateRequest, SimulateResponse
from app.services.simulation import calculate_simulation

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("", response_model=SimulateResponse)
async def simulate_intervention(payload: SimulateRequest):
    """
    Run what-if energy savings calculator for an intervention type with custom parameters.
    Returns baseline vs projected kWh, monthly rupee savings, and payback period.
    """
    try:
        result = calculate_simulation(payload.intervention_type, payload.params)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
