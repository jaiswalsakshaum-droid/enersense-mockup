import joblib
import pandas as pd


# =========================================================
# Model paths
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


# =========================================================
# Load models
# =========================================================

print("Loading EnnerSense ML models...")

energy_model = joblib.load(
    ENERGY_MODEL_PATH
)

production_model = joblib.load(
    PRODUCTION_MODEL_PATH
)

quality_model = joblib.load(
    QUALITY_MODEL_PATH
)

print("All models loaded successfully.")


# =========================================================
# Scenario simulator
# =========================================================

def simulate_scenario(
    machine_id,
    product_id,
    load_percent,
    speed_percent,
    ambient_temperature_c,
    machine_temperature_c,
    maintenance_age_days,
    cycle_time_sec,
    shift,
):
    """
    Simulate factory performance under
    a proposed operating condition.
    """

    scenario = pd.DataFrame(
        [
            {
                "machine_id": machine_id,
                "product_id": product_id,
                "load_percent": load_percent,
                "speed_percent": speed_percent,
                "ambient_temperature_c": ambient_temperature_c,
                "machine_temperature_c": machine_temperature_c,
                "maintenance_age_days": maintenance_age_days,
                "cycle_time_sec": cycle_time_sec,
                "shift": shift,
            }
        ]
    )

    # -----------------------------------------------------
    # Predictions
    # -----------------------------------------------------

    predicted_energy = energy_model.predict(
        scenario
    )[0]

    predicted_production = production_model.predict(
        scenario
    )[0]

    predicted_defect_rate = quality_model.predict(
        scenario
    )[0]

    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    result = {
        "machine_id": machine_id,
        "product_id": product_id,
        "load_percent": load_percent,
        "speed_percent": speed_percent,
        "predicted_energy_kwh": round(
            float(predicted_energy),
            3,
        ),
        "predicted_production_units": round(
            float(predicted_production),
            2,
        ),
        "predicted_defect_rate": round(
            float(predicted_defect_rate),
            5,
        ),
    }

    return result


# =========================================================
# Test scenario
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("ENNERSENSE — SCENARIO SIMULATOR")
    print("=" * 70)

    result = simulate_scenario(
        machine_id="HEAT_01",
        product_id="P001",
        load_percent=82,
        speed_percent=85,
        ambient_temperature_c=28,
        machine_temperature_c=75,
        maintenance_age_days=30,
        cycle_time_sec=45,
        shift="Morning",
    )

    print("\nSCENARIO RESULT")
    print("-" * 40)

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)