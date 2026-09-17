import joblib
import pandas as pd


# =========================================================
# Load trained models
# =========================================================

ENERGY_MODEL_PATH = "trained_models/energy_prediction_model.joblib"
PRODUCTION_MODEL_PATH = "trained_models/production_prediction_model.joblib"
QUALITY_MODEL_PATH = "trained_models/quality_prediction_model.joblib"

energy_model = joblib.load(ENERGY_MODEL_PATH)
production_model = joblib.load(PRODUCTION_MODEL_PATH)
quality_model = joblib.load(QUALITY_MODEL_PATH)


# =========================================================
# Feature preparation
# =========================================================

def prepare_input(
    machine_id,
    product_id,
    load_percent,
    speed_percent,
    ambient_temperature_c,
    machine_temperature_c,
    maintenance_age_days,
    cycle_time_sec,
    shift
):
    return pd.DataFrame([{
        "machine_id": machine_id,
        "product_id": product_id,
        "load_percent": load_percent,
        "speed_percent": speed_percent,
        "ambient_temperature_c": ambient_temperature_c,
        "machine_temperature_c": machine_temperature_c,
        "maintenance_age_days": maintenance_age_days,
        "cycle_time_sec": cycle_time_sec,
        "shift": shift
    }])


# =========================================================
# Predict one operating state
# =========================================================

def predict_state(
    machine_id,
    product_id,
    load_percent,
    speed_percent,
    ambient_temperature_c,
    machine_temperature_c,
    maintenance_age_days,
    cycle_time_sec,
    shift
):

    data = prepare_input(
        machine_id,
        product_id,
        load_percent,
        speed_percent,
        ambient_temperature_c,
        machine_temperature_c,
        maintenance_age_days,
        cycle_time_sec,
        shift
    )

    energy = energy_model.predict(data)[0]
    production = production_model.predict(data)[0]
    defect = quality_model.predict(data)[0]

    energy_per_unit = (
        energy / production
        if production > 0
        else 0
    )

    return {
        "load_percent": load_percent,
        "speed_percent": speed_percent,
        "energy_kwh": float(energy),
        "production_units": float(production),
        "defect_rate": float(defect),
        "defect_percentage": float(defect * 100),
        "energy_per_unit": float(energy_per_unit)
    }


# =========================================================
# What-If Simulation
# =========================================================

def simulate_what_if(
    machine_id,
    product_id,

    current_load_percent,
    current_speed_percent,

    what_if_load_percent,
    what_if_speed_percent,

    ambient_temperature_c,
    machine_temperature_c,
    maintenance_age_days,
    cycle_time_sec,
    shift
):

    # -----------------------------------------------------
    # Current operating state
    # -----------------------------------------------------

    current = predict_state(
        machine_id,
        product_id,
        current_load_percent,
        current_speed_percent,
        ambient_temperature_c,
        machine_temperature_c,
        maintenance_age_days,
        cycle_time_sec,
        shift
    )

    # -----------------------------------------------------
    # What-if operating state
    # -----------------------------------------------------

    what_if = predict_state(
        machine_id,
        product_id,
        what_if_load_percent,
        what_if_speed_percent,
        ambient_temperature_c,
        machine_temperature_c,
        maintenance_age_days,
        cycle_time_sec,
        shift
    )

    # -----------------------------------------------------
    # Calculate impact
    # -----------------------------------------------------

    energy_change = (
        what_if["energy_kwh"]
        - current["energy_kwh"]
    )

    energy_saved = max(
        current["energy_kwh"] - what_if["energy_kwh"],
        0
    )

    energy_saving_percent = (
        energy_saved / current["energy_kwh"] * 100
        if current["energy_kwh"] > 0
        else 0
    )

    production_change_percent = (
        (
            what_if["production_units"]
            - current["production_units"]
        )
        / current["production_units"]
        * 100
        if current["production_units"] > 0
        else 0
    )

    defect_change_percent = (
        (
            what_if["defect_rate"]
            - current["defect_rate"]
        )
        / current["defect_rate"]
        * 100
        if current["defect_rate"] > 0
        else 0
    )

    # -----------------------------------------------------
    # Recommendation message
    # -----------------------------------------------------

    if (
        what_if["energy_kwh"] < current["energy_kwh"]
        and what_if["production_units"] >= current["production_units"]
        and what_if["defect_rate"] <= current["defect_rate"]
    ):
        recommendation = "Recommended: lower energy with no production or quality penalty."

    elif what_if["energy_kwh"] < current["energy_kwh"]:
        recommendation = "Energy decreases, but check production and quality impact before applying."

    elif what_if["energy_kwh"] > current["energy_kwh"]:
        recommendation = "Not energy efficient compared with the current operating state."

    else:
        recommendation = "Operating change has limited energy benefit."

    return {
        "machine_id": machine_id,
        "product_id": product_id,

        "current_state": current,

        "what_if_state": what_if,

        "impact": {
            "energy_change_kwh": round(energy_change, 3),
            "energy_saved_kwh": round(energy_saved, 3),
            "energy_saving_percent": round(
                energy_saving_percent,
                2
            ),
            "production_change_percent": round(
                production_change_percent,
                2
            ),
            "defect_change_percent": round(
                defect_change_percent,
                2
            )
        },

        "recommendation": recommendation
    }


# =========================================================
# Local test
# =========================================================

if __name__ == "__main__":

    result = simulate_what_if(

        machine_id="HEAT_01",
        product_id="P001",

        current_load_percent=90,
        current_speed_percent=80,

        what_if_load_percent=78,
        what_if_speed_percent=95,

        ambient_temperature_c=30,
        machine_temperature_c=70,
        maintenance_age_days=60,
        cycle_time_sec=60,
        shift="A"
    )

    print("\n========================================")
    print("       ENNERSENSE WHAT-IF ENGINE")
    print("========================================")

    print("\nCURRENT STATE")
    print(result["current_state"])

    print("\nWHAT-IF STATE")
    print(result["what_if_state"])

    print("\nIMPACT")
    print(result["impact"])

    print("\nRECOMMENDATION")
    print(result["recommendation"])