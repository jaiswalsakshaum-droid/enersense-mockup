from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd

from src.api.intelligence import get_intelligence
from src.analysis.decision_engine import build_decision
from src.simulation.simulate import simulate_what_if
from src.simulation.counterfactual_explorer import explore_counterfactuals

# =========================================================
# EnnerSense ML API
# =========================================================

app = FastAPI(
    title="EnerSense ML Engine",
    description="AI-powered industrial energy and production optimization",
    version="1.0.0",
)


# =========================================================
# Load trained models
# =========================================================

ENERGY_MODEL_PATH = (
    "trained_models/energy_prediction_model.joblib"
)

PRODUCTION_MODEL_PATH = (
    "trained_models/production_prediction_model.joblib"
)

QUALITY_MODEL_PATH = (
    "trained_models/quality_prediction_model.joblib"
)


energy_model = joblib.load(
    ENERGY_MODEL_PATH
)

production_model = joblib.load(
    PRODUCTION_MODEL_PATH
)

quality_model = joblib.load(
    QUALITY_MODEL_PATH
)

# ============================================================
# Valid machine / product IDs
# ============================================================

SCENARIO_DATA_PATH = "data/scenario_predictions.csv"

scenario_data = pd.read_csv(SCENARIO_DATA_PATH)

VALID_MACHINE_IDS = set(
    scenario_data["machine_id"].astype(str).str.strip()
)

VALID_PRODUCT_IDS = set(
    scenario_data["product_id"].astype(str).str.strip()
)

# =========================================================
# Request schema
# =========================================================

class PredictionRequest(BaseModel):

    machine_id: str
    product_id: str

    load_percent: float = Field(..., ge=0, le=100)
    speed_percent: float = Field(..., ge=0, le=100)

    ambient_temperature_c: float = Field(..., ge=-50, le=100)
    machine_temperature_c: float = Field(..., ge=-50, le=200)

    maintenance_age_days: float = Field(..., ge=0)
    cycle_time_sec: float = Field(..., gt=0)

    shift: str


# ============================================================
# Input validation helper
# ============================================================

def validate_machine_product(
    machine_id: str,
    product_id: str
):
    machine_id = str(machine_id).strip()
    product_id = str(product_id).strip()

    if machine_id not in VALID_MACHINE_IDS:
        return {
            "valid": False,
            "error": f"Unknown machine_id: {machine_id}"
        }

    if product_id not in VALID_PRODUCT_IDS:
        return {
            "valid": False,
            "error": f"Unknown product_id: {product_id}"
        }

    return {
        "valid": True
    }

class CounterfactualRequest(BaseModel):
    machine_id: str
    product_id: str
    load_percent: float = Field(..., ge=0, le=100)
    speed_percent: float = Field(..., ge=0, le=100)
    ambient_temperature_c: float = 30
    machine_temperature_c: float = 70
    maintenance_age_days: float = 60
    cycle_time_sec: float = 60
    shift: str = "A"

class WhatIfRequest(BaseModel):
    machine_id: str
    product_id: str
    
    current_load_percent: float = Field(..., ge=0, le=100)
    current_speed_percent: float = Field(..., ge=0, le=100)

    what_if_load_percent: float = Field(..., ge=0, le=100)
    what_if_speed_percent: float = Field(..., ge=0, le=100)

    ambient_temperature_c: float
    machine_temperature_c: float
    maintenance_age_days: float = Field(..., ge=0)
    cycle_time_sec: float = Field(..., gt=0)
    shift: str


# =========================================================
# Health check
# =========================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "EnnerSense ML Engine",
        "models": [
            "energy",
            "production",
            "quality",
        ],
    }


# =========================================================
# Prediction endpoint
# =========================================================

@app.post("/predict")
async def predict(
    request: PredictionRequest
):

    validation = validate_machine_product(
        request.machine_id,
        request.product_id
    )

    if not validation["valid"]:
        return {
            "status": "ERROR",
            "machine_id": request.machine_id,
            "product_id": request.product_id,
            "error": validation["error"]
        }
    
    if request.machine_id not in VALID_MACHINE_IDS:
        return {
            "status": "error",
            "message": f"Unknown machine_id: {request.machine_id}"
        }

    if request.product_id not in VALID_PRODUCT_IDS:
        return {
            "status": "error",
            "message": f"Unknown product_id: {request.product_id}"
        }

    data = pd.DataFrame(
        [
            request.model_dump()
        ]
    )

    energy = energy_model.predict(
        data
    )[0]

    production = production_model.predict(
        data
    )[0]

    defect = quality_model.predict(
        data
    )[0]

    energy_per_unit = (
        energy / production
        if production > 0
        else 0
    )

    return {

        "machine_id":
            request.machine_id,

        "product_id":
            request.product_id,

        "predictions": {

            "energy_kwh":
                round(float(energy), 3),

            "production_units":
                round(float(production), 2),

            "defect_rate":
                round(float(defect), 5),

            "defect_percentage":
                round(float(defect) * 100, 3),

            "energy_per_unit":
                round(float(energy_per_unit), 5),
        }
    }

# ============================================================
# Intelligence endpoint
# ============================================================

@app.post("/intelligence")
async def intelligence(request: PredictionRequest):

    return get_intelligence(
        request.model_dump()
    )

# ============================================================
# Unified EnnerSense Analysis Endpoint
# ============================================================

@app.post("/analyze")
async def analyze(request: PredictionRequest):

    # Get ML predictions
    predictions = await predict(request)

    # Get intelligence insights
    intelligence = get_intelligence(
        request.model_dump()
    )

    decision = build_decision(
      current_energy=predictions["predictions"]["energy_kwh"],
        current_production=predictions["predictions"]["production_units"],
        current_defect=predictions["predictions"]["defect_rate"],
        current_load=request.load_percent,
        current_speed=request.speed_percent,
        energy_debt=intelligence["energy_debt"]["energy_debt_kwh"],
        energy_debt_percent=intelligence["energy_debt"]["energy_debt_percent"],
        avoidable_cost=intelligence["energy_debt"]["avoidable_cost_inr"],
        dna_severity=intelligence["process_dna"]["severity"],
        cascade_type=intelligence["cascade"]["type"],
        cascade_severity=intelligence["cascade"]["severity"],
    )

    return {
    "status": "success",
    "machine_id": request.machine_id,
    "product_id": request.product_id,
    "predictions": predictions,
    "intelligence": intelligence,
    "decision": decision
}


@app.post("/simulate")
async def simulate(request: WhatIfRequest):

    result = simulate_what_if(
        machine_id=request.machine_id,
        product_id=request.product_id,

        current_load_percent=request.current_load_percent,
        current_speed_percent=request.current_speed_percent,

        what_if_load_percent=request.what_if_load_percent,
        what_if_speed_percent=request.what_if_speed_percent,

        ambient_temperature_c=request.ambient_temperature_c,
        machine_temperature_c=request.machine_temperature_c,
        maintenance_age_days=request.maintenance_age_days,
        cycle_time_sec=request.cycle_time_sec,
        shift=request.shift
    )

    return result


@app.post("/counterfactual")
async def counterfactual(request: CounterfactualRequest):

    result = explore_counterfactuals(
    machine_id=request.machine_id,
    product_id=request.product_id,
    current_load_percent=request.load_percent,
    current_speed_percent=request.speed_percent,
    ambient_temperature_c=request.ambient_temperature_c,
    machine_temperature_c=request.machine_temperature_c,
    maintenance_age_days=request.maintenance_age_days,
    cycle_time_sec=request.cycle_time_sec,
    shift=request.shift,
)

    return result