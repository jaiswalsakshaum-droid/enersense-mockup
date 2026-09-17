import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

RISK_PATH = BASE_DIR / "data" / "risk_aware_recommendation.csv"
ENERGY_DEBT_PATH = BASE_DIR / "data" / "energy_debt_report.csv"


def build_decision(
    current_energy,
    current_production,
    current_defect,
    current_load,
    current_speed,
    energy_debt,
    energy_debt_percent,
    avoidable_cost,
    dna_severity,
    cascade_type,
    cascade_severity,
):
    """
    Convert EnnerSense ML signals into one operator-facing decision.
    """

    # --------------------------------------------------
    # Load risk-aware recommendations
    # --------------------------------------------------

    risk_df = pd.read_csv(RISK_PATH)

    if risk_df.empty:
        return {
            "status": "NO_RECOMMENDATION",
            "message": "No feasible operating recommendation found."
        }

    # Best robust operating point
    best = risk_df.iloc[0]

    recommended_load = float(best["load_percent"])
    recommended_speed = float(best["speed_percent"])

    recommended_energy = float(best["predicted_energy_kwh"])
    recommended_production = float(
        best["predicted_production_units"]
    )
    recommended_defect = float(
        best["predicted_defect_rate"]
    )

    recommended_energy_per_unit = float(
        best["energy_per_unit"]
    )

    risk_score = float(best["risk_score"])

    uncertainty = float(
        best["energy_uncertainty_percent"]
    )

    robust_score = float(
        best["robust_score"]
    )

    # --------------------------------------------------
    # Expected savings
    # --------------------------------------------------

    energy_saving = max(
        0,
        current_energy - recommended_energy
    )

    if current_energy > 0:
        saving_percent = (
            energy_saving / current_energy
        ) * 100
    else:
        saving_percent = 0

    # --------------------------------------------------
    # Determine overall status
    # --------------------------------------------------

    if energy_debt_percent >= 40:
        status = "HIGH_ENERGY_INEFFICIENCY"

    elif energy_debt_percent >= 20:
        status = "ENERGY_INEFFICIENCY"

    elif dna_severity in ["WARNING", "CRITICAL"]:
        status = "PROCESS_DRIFT"

    else:
        status = "OPTIMIZED"

    # --------------------------------------------------
    # Build operator message
    # --------------------------------------------------

    if energy_debt > 0:

        action = (
            f"Shift operating point from "
            f"{current_load:.0f}% load / "
            f"{current_speed:.0f}% speed toward "
            f"{recommended_load:.0f}% load / "
            f"{recommended_speed:.0f}% speed."
        )

    else:

        action = (
            "Current operating conditions are "
            "close to the recommended operating point."
        )

    # --------------------------------------------------
    # Return final decision
    # --------------------------------------------------

    return {

        "status": status,

        "current_state": {
            "load_percent": round(current_load, 2),
            "speed_percent": round(current_speed, 2),
            "energy_kwh": round(current_energy, 3),
            "production_units": round(
                current_production, 2
            ),
            "defect_rate": round(
                current_defect, 5
            ),
        },

        "energy_impact": {
            "energy_debt_kwh": round(
                energy_debt, 3
            ),
            "energy_debt_percent": round(
                energy_debt_percent, 2
            ),
            "avoidable_cost_inr": round(
                avoidable_cost, 2
            ),
        },

        "recommended_state": {
            "load_percent": round(
                recommended_load, 2
            ),
            "speed_percent": round(
                recommended_speed, 2
            ),
            "energy_kwh": round(
                recommended_energy, 3
            ),
            "production_units": round(
                recommended_production, 2
            ),
            "defect_rate": round(
                recommended_defect, 5
            ),
            "energy_per_unit": round(
                recommended_energy_per_unit, 5
            ),
        },

        "expected_impact": {
            "energy_saving_kwh": round(
                energy_saving, 3
            ),
            "energy_saving_percent": round(
                saving_percent, 2
            ),
        },

        "risk": {
            "risk_score": round(
                risk_score, 2
            ),
            "uncertainty_percent": round(
                uncertainty, 2
            ),
            "robust_score": round(
                robust_score, 4
            ),
        },

        "signals": {
            "dna_severity": dna_severity,
            "cascade_type": cascade_type,
            "cascade_severity": cascade_severity,
        },

        "action": action,
    }