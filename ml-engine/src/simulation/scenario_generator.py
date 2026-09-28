import pandas as pd
import joblib
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "raw" / "factory_production_data.csv"

ENERGY_MODEL_PATH = (
    BASE_DIR / "trained_models" / "energy_prediction_model.joblib"
)

PRODUCTION_MODEL_PATH = (
    BASE_DIR / "trained_models" / "production_prediction_model.joblib"
)

QUALITY_MODEL_PATH = (
    BASE_DIR / "trained_models" / "quality_prediction_model.joblib"
)

OUTPUT_PATH = (
    BASE_DIR / "data" / "scenario_predictions.csv"
)


# ============================================================
# SCENARIO VALUES
# ============================================================

LOAD_VALUES = [50, 60, 70, 80, 90, 100]
SPEED_VALUES = [60, 70, 80, 90, 100]


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():

    print("Loading trained models...")

    energy_model = joblib.load(ENERGY_MODEL_PATH)
    production_model = joblib.load(PRODUCTION_MODEL_PATH)
    quality_model = joblib.load(QUALITY_MODEL_PATH)

    print("Models loaded successfully.")

    return (
        energy_model,
        production_model,
        quality_model,
    )


# ============================================================
# GENERATE SCENARIOS
# ============================================================

def generate_scenarios():

    print("=" * 70)
    print("ENNERSENSE — SCENARIO PREDICTION GENERATOR")
    print("=" * 70)

    print("\nLoading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset shape: {df.shape}")

    energy_model, production_model, quality_model = load_models()

    # --------------------------------------------------------
    # Get representative values
    # --------------------------------------------------------

    machines = sorted(df["machine_id"].unique())
    products = sorted(df["product_id"].unique())

    print("\nMachines:")
    print(machines)

    print("\nProducts:")
    print(products)

    scenarios = []

    # --------------------------------------------------------
    # Generate operating scenarios
    # --------------------------------------------------------

    for machine_id in machines:

        for product_id in products:

            # Get representative row for machine/product
            subset = df[
                (df["machine_id"] == machine_id)
                & (df["product_id"] == product_id)
            ]

            if subset.empty:
                continue

            base = subset.iloc[0]

            for load in LOAD_VALUES:

                for speed in SPEED_VALUES:

                    scenario = {
                        "machine_id": machine_id,
                        "product_id": product_id,

                        "load_percent": load,
                        "speed_percent": speed,

                        "ambient_temperature_c":
                            float(
                                subset[
                                    "ambient_temperature_c"
                                ].mean()
                            ),

                        "machine_temperature_c":
                            float(
                                subset[
                                    "machine_temperature_c"
                                ].mean()
                            ),

                        "maintenance_age_days":
                            float(
                                subset[
                                    "maintenance_age_days"
                                ].mean()
                            ),

                        "cycle_time_sec":
                            float(
                                subset[
                                    "cycle_time_sec"
                                ].mean()
                            ),

                        "shift":
                            base["shift"],
                    }

                    scenarios.append(scenario)

    scenario_df = pd.DataFrame(scenarios)

    print(
        f"\nGenerated scenarios: "
        f"{len(scenario_df):,}"
    )

    # ========================================================
    # MODEL PREDICTIONS
    # ========================================================

    print("\nGenerating predictions...")

    energy_predictions = energy_model.predict(
        scenario_df
    )

    production_predictions = production_model.predict(
        scenario_df
    )

    quality_predictions = quality_model.predict(
        scenario_df
    )

    scenario_df["predicted_energy_kwh"] = (
        energy_predictions
    )

    scenario_df["predicted_production_units"] = (
        production_predictions
    )

    scenario_df["predicted_defect_rate"] = (
        quality_predictions
    )

    # ========================================================
    # ENERGY PER UNIT
    # ========================================================

    scenario_df["energy_per_unit"] = (
        scenario_df["predicted_energy_kwh"]
        /
        scenario_df["predicted_production_units"]
        .replace(0, 1)
    )

    # ========================================================
    # PREDICTED ENERGY COST
    # ========================================================

    # Use average electricity price from dataset

    average_price = (
        df["electricity_price_inr_per_kwh"]
        .mean()
    )

    scenario_df["predicted_energy_cost_inr"] = (
        scenario_df["predicted_energy_kwh"]
        * average_price
    )

    # ========================================================
    # ROUND VALUES
    # ========================================================

    scenario_df["predicted_energy_kwh"] = (
        scenario_df["predicted_energy_kwh"]
        .round(3)
    )

    scenario_df["predicted_production_units"] = (
        scenario_df["predicted_production_units"]
        .round(2)
    )

    scenario_df["predicted_defect_rate"] = (
        scenario_df["predicted_defect_rate"]
        .round(6)
    )

    scenario_df["energy_per_unit"] = (
        scenario_df["energy_per_unit"]
        .round(5)
    )

    scenario_df["predicted_energy_cost_inr"] = (
        scenario_df["predicted_energy_cost_inr"]
        .round(2)
    )

    # ========================================================
    # SAVE
    # ========================================================

    scenario_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 70)
    print("SCENARIO GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal scenarios: "
        f"{len(scenario_df):,}"
    )

    print(
        f"\nSaved to:\n"
        f"{OUTPUT_PATH}"
    )

    print("\nSample scenarios:")

    print(
        scenario_df.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    generate_scenarios()