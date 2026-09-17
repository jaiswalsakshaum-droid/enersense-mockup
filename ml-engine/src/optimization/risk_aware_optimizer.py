import pandas as pd
import numpy as np
from pathlib import Path
import joblib


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SCENARIO_FILE = (
    BASE_DIR
    / "data"
    / "feasible_scenarios.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "risk_aware_recommendation.csv"
)

RF_MODEL_FILE = (
    BASE_DIR
    / "trained_models"
    / "energy_prediction_model.joblib"
)

XGB_MODEL_FILE = (
    BASE_DIR
    / "trained_models"
    / "energy_xgboost_model.joblib"
)


# ============================================================
# CONFIGURATION
# ============================================================

# How strongly uncertainty affects the final score.
RISK_WEIGHT = 0.25


# ============================================================
# LOAD DATA
# ============================================================

def load_scenarios():

    df = pd.read_csv(
        SCENARIO_FILE
    )

    print(
        f"Loaded {len(df)} feasible scenarios"
    )

    return df


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():

    print("\nLoading energy models...")

    rf_model = joblib.load(
        RF_MODEL_FILE
    )

    xgb_model = joblib.load(
        XGB_MODEL_FILE
    )

    print("Random Forest model loaded")
    print("XGBoost model loaded")

    return rf_model, xgb_model


# ============================================================
# PREPARE MODEL INPUT
# ============================================================

def prepare_features(df):

    """
    Prepare the same features used by the
    energy prediction models.
    """

    feature_columns = [
        "machine_id",
        "product_id",
        "shift",
        "load_percent",
        "speed_percent",
        "ambient_temperature_c",
        "machine_temperature_c",
        "maintenance_age_days",
        "cycle_time_sec"
    ]

    missing = [
        col
        for col in feature_columns
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing model features: {missing}"
        )

    X = df[
        feature_columns
    ].copy()

    return X


# ============================================================
# CALCULATE MODEL DISAGREEMENT
# ============================================================

def calculate_uncertainty(
    df,
    rf_model,
    xgb_model
):

    X = prepare_features(df)

    # Predictions from both models
    rf_prediction = rf_model.predict(X)

    xgb_prediction = xgb_model.predict(X)

    df = df.copy()

    df["rf_energy_prediction"] = (
        rf_prediction
    )

    df["xgb_energy_prediction"] = (
        xgb_prediction
    )

    # Absolute disagreement
    df["energy_model_disagreement"] = np.abs(
        rf_prediction - xgb_prediction
    )

    # Percentage disagreement
    df["energy_uncertainty_percent"] = (
        df["energy_model_disagreement"]
        /
        np.maximum(
            np.abs(rf_prediction),
            0.001
        )
        * 100
    )

    return df


# ============================================================
# NORMALIZE RISK
# ============================================================

def normalize_risk(df):

    max_uncertainty = (
        df["energy_uncertainty_percent"]
        .max()
    )

    if max_uncertainty == 0:

        df["risk_score"] = 0

    else:

        df["risk_score"] = (
            df["energy_uncertainty_percent"]
            / max_uncertainty
            * 100
        )

    return df


# ============================================================
# ROBUST ENERGY SCORE
# ============================================================

def calculate_robust_score(df):

    """
    Lower is better.

    Combines:

        Energy efficiency
        +
        Prediction uncertainty

    Energy efficiency is based on
    energy consumed per produced unit.
    """

    # Normalize energy efficiency
    energy_min = (
        df["energy_per_unit"].min()
    )

    energy_max = (
        df["energy_per_unit"].max()
    )

    if energy_max == energy_min:

        df["normalized_energy"] = 0

    else:

        df["normalized_energy"] = (
            (
                df["energy_per_unit"]
                - energy_min
            )
            /
            (
                energy_max
                - energy_min
            )
        )

    # Normalize risk
    df["normalized_risk"] = (
        df["risk_score"] / 100
    )

    # Final robust score
    df["robust_score"] = (
        (1 - RISK_WEIGHT)
        * df["normalized_energy"]
        +
        RISK_WEIGHT
        * df["normalized_risk"]
    )

    return df


# ============================================================
# SELECT RECOMMENDATION
# ============================================================

def select_recommendation(df):

    df = df.sort_values(
        "robust_score",
        ascending=True
    ).copy()

    df["risk_rank"] = range(
        1,
        len(df) + 1
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("       ENNERSENSE RISK-AWARE OPTIMIZATION ENGINE")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    scenarios = load_scenarios()

    rf_model, xgb_model = load_models()

    # --------------------------------------------------------
    # Calculate uncertainty
    # --------------------------------------------------------

    print("\nCalculating model uncertainty...")

    scenarios = calculate_uncertainty(
        scenarios,
        rf_model,
        xgb_model
    )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    scenarios = normalize_risk(
        scenarios
    )

    # --------------------------------------------------------
    # Robust score
    # --------------------------------------------------------

    scenarios = calculate_robust_score(
        scenarios
    )

    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    ranked = select_recommendation(
        scenarios
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    ranked.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Best recommendation
    # --------------------------------------------------------

    best = ranked.iloc[0]

    print("\n" + "-" * 70)
    print("ROBUST RECOMMENDED OPERATING PLAN")
    print("-" * 70)

    print(
        f"Machine              : "
        f"{best['machine_id']}"
    )

    print(
        f"Product              : "
        f"{best['product_id']}"
    )

    print(
        f"Load                 : "
        f"{best['load_percent']:.1f}%"
    )

    print(
        f"Speed                : "
        f"{best['speed_percent']:.1f}%"
    )

    print(
        f"Predicted Energy     : "
        f"{best['predicted_energy_kwh']:.2f} kWh"
    )

    print(
        f"Energy / Unit       : "
        f"{best['energy_per_unit']:.4f} kWh/unit"
    )

    print(
        f"Production           : "
        f"{best['predicted_production_units']:.2f}"
    )

    print(
        f"Defect Rate          : "
        f"{best['predicted_defect_rate'] * 100:.2f}%"
    )

    print(
        f"RF Energy Prediction : "
        f"{best['rf_energy_prediction']:.2f} kWh"
    )

    print(
        f"XGB Energy Prediction: "
        f"{best['xgb_energy_prediction']:.2f} kWh"
    )

    print(
        f"Model Disagreement   : "
        f"{best['energy_model_disagreement']:.2f} kWh"
    )

    print(
        f"Uncertainty          : "
        f"{best['energy_uncertainty_percent']:.2f}%"
    )

    print(
        f"Risk Score           : "
        f"{best['risk_score']:.2f}/100"
    )

    print(
        f"Robust Score         : "
        f"{best['robust_score']:.4f}"
    )

    print(
        f"Risk Rank            : "
        f"{int(best['risk_rank'])}"
    )

    # --------------------------------------------------------
    # Top 10
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("TOP 10 ROBUST OPERATING SCENARIOS")
    print("-" * 70)

    columns = [
        "machine_id",
        "load_percent",
        "speed_percent",
        "predicted_energy_kwh",
        "energy_per_unit",
        "predicted_production_units",
        "predicted_defect_rate",
        "energy_uncertainty_percent",
        "risk_score",
        "robust_score"
    ]

    print(
        ranked[
            columns
        ]
        .head(10)
        .round(4)
        .to_string(index=False)
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print("=" * 70)


if __name__ == "__main__":
    main()