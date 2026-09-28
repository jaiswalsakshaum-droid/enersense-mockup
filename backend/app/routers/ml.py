from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ml_engine import (
    analyze_with_ml,
    simulate_with_ml,
    counterfactual_with_ml,
)


router = APIRouter(
    prefix="/api/ml",
    tags=["ML Intelligence"]
)


# ============================================================
# ANALYZE REQUEST
# ============================================================

class MLAnalyzeRequest(BaseModel):

    machine_id: str
    product_id: str

    load_percent: float
    speed_percent: float

    ambient_temperature_c: float
    machine_temperature_c: float

    maintenance_age_days: float
    cycle_time_sec: float

    shift: str


# ============================================================
# SIMULATION REQUEST
# ============================================================

class MLSimulateRequest(BaseModel):

    machine_id: str
    product_id: str

    current_load_percent: float
    current_speed_percent: float

    what_if_load_percent: float
    what_if_speed_percent: float

    ambient_temperature_c: float
    machine_temperature_c: float

    maintenance_age_days: float
    cycle_time_sec: float

    shift: str


# ============================================================
# COUNTERFACTUAL REQUEST
# ============================================================

class MLCounterfactualRequest(BaseModel):

    machine_id: str
    product_id: str

    load_percent: float
    speed_percent: float

    ambient_temperature_c: float = 30
    machine_temperature_c: float = 70

    maintenance_age_days: float = 60
    cycle_time_sec: float = 60

    shift: str = "A"


# ============================================================
# ANALYZE
# ============================================================

@router.post("/analyze")
def analyze(request: MLAnalyzeRequest):

    try:

        return analyze_with_ml(
            request.model_dump()
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )


# ============================================================
# SIMULATE
# ============================================================

@router.post("/simulate")
def simulate(request: MLSimulateRequest):

    try:

        return simulate_with_ml(
            request.model_dump()
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )


# ============================================================
# COUNTERFACTUAL
# ============================================================

@router.post("/counterfactual")
def counterfactual(
    request: MLCounterfactualRequest
):

    try:

        return counterfactual_with_ml(
            request.model_dump()
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )