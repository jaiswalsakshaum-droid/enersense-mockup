from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd


# =========================================================
# EnnerSense ML API
# =========================================================

app = FastAPI(
    title="EnnerSense ML Engine",
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


# =========================================================
# Request schema
# =========================================================

class PredictionRequest(BaseModel):

    machine_id: str
    product_id: str

    load_percent: float
    speed_percent: float

    ambient_temperature_c: float
    machine_temperature_c: float

    maintenance_age_days: float
    cycle_time_sec: float

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