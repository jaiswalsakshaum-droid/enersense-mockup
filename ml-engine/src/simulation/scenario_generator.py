import itertools
import pandas as pd
import joblib


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

print("Loading EnnerSense models...")

energy_model = joblib.load(
    ENERGY_MODEL_PATH
)

production_model = joblib.load(
    PRODUCTION_MODEL_PATH
)

quality_model = joblib.load(
    QUALITY_MODEL_PATH
)

print("Models loaded.")


# =========================================================
# Generate scenarios
# =========================================================

def generate_scenarios(
    machine_id="HEAT_01",
    product_id="P001",
    shift="Morning",
    ambient_temperature_c=28,
    maintenance_age_days=30,
    cycle_time_sec=45,
):
    """
    Generate possible operating scenarios.
    """

    loads = range(70, 101, 2)

    speeds = range(75, 101, 5)

    scenarios = []

    for load, speed in itertools.product(
        loads,
        speeds,
    ):

        # Approximate machine temperature
        # for the proposed operating condition.

        machine_temperature = (
            42
            + 0.30 * load
            + 0.10 * ambient_temperature_c
            + 0.015
            * max(load - 80, 0) ** 2
        )

        scenarios.append(
            {
                "machine_id": machine_id,
                "product_id": product_id,
                "load_percent": load,
                "speed_percent": speed,
                "ambient_temperature_c": ambient_temperature_c,
                "machine_temperature_c": machine_temperature,
                "maintenance_age_days": maintenance_age_days,
                "cycle_time_sec": cycle_time_sec,
                "shift": shift,
            }
        )

    return pd.DataFrame(scenarios)


# =========================================================
# Evaluate scenarios
# =========================================================

def evaluate_scenarios(df):

    predictions = df.copy()

    predictions["predicted_energy_kwh"] = (
        energy_model.predict(df)
    )

    predictions["predicted_production_units"] = (
        production_model.predict(df)
    )

    predictions["predicted_defect_rate"] = (
        quality_model.predict(df)
    )

    return predictions


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("ENNERSENSE — SCENARIO GENERATOR")
    print("=" * 70)

    scenarios = generate_scenarios()

    print(
        f"\nGenerated scenarios: {len(scenarios):,}"
    )

    results = evaluate_scenarios(
        scenarios
    )

    # -----------------------------------------------------
    # Calculate energy per unit
    # -----------------------------------------------------

    results["energy_per_unit"] = (
        results["predicted_energy_kwh"]
        / results["predicted_production_units"]
    )

    # -----------------------------------------------------
    # Calculate estimated cost
    # -----------------------------------------------------

    electricity_price = 8.5

    results["predicted_energy_cost_inr"] = (
        results["predicted_energy_kwh"]
        * electricity_price
    )

    # -----------------------------------------------------
    # Sort by energy efficiency
    # -----------------------------------------------------

    results = results.sort_values(
        "energy_per_unit"
    )

    # -----------------------------------------------------
    # Display top scenarios
    # -----------------------------------------------------

    print("\nTOP 10 ENERGY-EFFICIENT SCENARIOS")
    print("-" * 70)

    columns = [
        "load_percent",
        "speed_percent",
        "predicted_energy_kwh",
        "predicted_production_units",
        "predicted_defect_rate",
        "energy_per_unit",
        "predicted_energy_cost_inr",
    ]

    print(
        results[columns]
        .head(10)
        .round(4)
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    output_path = (
        "data/scenario_predictions.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    print("\nScenario predictions saved to:")
    print(output_path)

    print("\n" + "=" * 70)
    print("SCENARIO GENERATION COMPLETE")
    print("=" * 70)