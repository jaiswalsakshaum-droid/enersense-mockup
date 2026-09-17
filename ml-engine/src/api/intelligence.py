import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SCENARIO_FILE = (
    BASE_DIR / "data" / "scenario_predictions.csv"
)

ENERGY_DEBT_FILE = (
    BASE_DIR / "data" / "energy_debt_report.csv"
)

DNA_FILE = (
    BASE_DIR / "data" / "dna_drift_report.csv"
)

CASCADE_FILE = (
    BASE_DIR / "data" / "cascade_alerts.csv"
)

RISK_FILE = (
    BASE_DIR / "data" / "risk_aware_recommendation.csv"
)


# ============================================================
# LOAD REPORTS
# ============================================================

def load_reports():

    scenarios = pd.read_csv(SCENARIO_FILE)
    energy_debt = pd.read_csv(ENERGY_DEBT_FILE)
    dna = pd.read_csv(DNA_FILE)
    cascade = pd.read_csv(CASCADE_FILE)
    risk = pd.read_csv(RISK_FILE)

    return scenarios, energy_debt, dna, cascade, risk


# ============================================================
# FIND CLOSEST SCENARIO
# ============================================================

def find_closest_scenario(request):

    scenarios = pd.read_csv(
        SCENARIO_FILE
    )

    # First restrict to same machine/product
    candidates = scenarios[
        (scenarios["machine_id"] == request["machine_id"])
        &
        (scenarios["product_id"] == request["product_id"])
    ].copy()

    if candidates.empty:
        return None

    # Calculate distance between requested state
    # and simulated states.
    candidates["distance"] = (
        (candidates["load_percent"]
         - request["load_percent"]).abs()
        +
        (candidates["speed_percent"]
         - request["speed_percent"]).abs()
        +
        (candidates["machine_temperature_c"]
         - request["machine_temperature_c"]).abs()
        * 0.5
        +
        (candidates["ambient_temperature_c"]
         - request["ambient_temperature_c"]).abs()
        * 0.2
        +
        (candidates["maintenance_age_days"]
         - request["maintenance_age_days"]).abs()
        * 0.1
        +
        (candidates["cycle_time_sec"]
         - request["cycle_time_sec"]).abs()
        * 0.1
    )

    closest = candidates.loc[
        candidates["distance"].idxmin()
    ]

    return closest


# ============================================================
# FIND INTELLIGENCE RECORD
# ============================================================

def find_record(
    df,
    machine_id,
    product_id,
    load_percent,
    speed_percent
):

    records = df[
        (df["machine_id"] == machine_id)
        &
        (df["product_id"] == product_id)
        &
        (df["load_percent"] == load_percent)
        &
        (df["speed_percent"] == speed_percent)
    ]

    if records.empty:
        return None

    return records.iloc[0]


# ============================================================
# BUILD INTELLIGENCE
# ============================================================

def get_intelligence(request):

    scenarios, energy_debt, dna, cascade, risk = (
        load_reports()
    )

    # Find closest simulated operating state
    scenario = find_closest_scenario(request)

    if scenario is None:

        return {
            "status": "not_found",
            "message": (
                "No simulated scenario exists for "
                "this machine and product."
            )
        }

    machine_id = scenario["machine_id"]
    product_id = scenario["product_id"]
    load = scenario["load_percent"]
    speed = scenario["speed_percent"]

    # --------------------------------------------------------
    # Energy Debt
    # --------------------------------------------------------

    debt = find_record(
        energy_debt,
        machine_id,
        product_id,
        load,
        speed
    )

    # --------------------------------------------------------
    # DNA Drift
    # --------------------------------------------------------

    dna_record = find_record(
        dna,
        machine_id,
        product_id,
        load,
        speed
    )

    # --------------------------------------------------------
    # Cascade
    # --------------------------------------------------------

    cascade_record = find_record(
        cascade,
        machine_id,
        product_id,
        load,
        speed
    )

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    response = {

        "machine_id": machine_id,

        "product_id": product_id,

        "operating_state": {

            "load_percent":
                float(load),

            "speed_percent":
                float(speed),

            "predicted_energy_kwh":
                round(
                    float(
                        scenario["predicted_energy_kwh"]
                    ),
                    3
                ),

            "predicted_production_units":
                round(
                    float(
                        scenario[
                            "predicted_production_units"
                        ]
                    ),
                    2
                ),

            "predicted_defect_rate":
                round(
                    float(
                        scenario[
                            "predicted_defect_rate"
                        ]
                    ),
                    5
                ),

            "energy_per_unit":
                round(
                    float(
                        scenario["energy_per_unit"]
                    ),
                    5
                )
        },

        "energy_debt": None,

        "process_dna": None,

        "cascade": None,

        "risk": None
    }

    # ========================================================
    # ENERGY DEBT
    # ========================================================

    if debt is not None:

        response["energy_debt"] = {

            "energy_debt_kwh":
                round(
                    float(
                        debt["energy_debt_kwh"]
                    ),
                    3
                ),

            "energy_debt_percent":
                round(
                    float(
                        debt["energy_debt_percent"]
                    ),
                    2
                ),

            "avoidable_cost_inr":
                round(
                    float(
                        debt["avoidable_cost_inr"]
                    ),
                    2
                ),

            "best_load_percent":
                float(
                    debt["best_load_percent"]
                ),

            "best_speed_percent":
                float(
                    debt["best_speed_percent"]
                ),

            "status":
                debt["status"]
        }

    # ========================================================
    # PROCESS DNA
    # ========================================================

    if dna_record is not None:

        response["process_dna"] = {

            "drift_score":
                round(
                    float(
                        dna_record[
                            "dna_drift_score"
                        ]
                    ),
                    2
                ),

            "severity":
                dna_record["severity"],

            "primary_issue":
                dna_record["primary_issue"],

            "explanation":
                dna_record["explanation"]
        }

    # ========================================================
    # CASCADE
    # ========================================================

    if cascade_record is not None:

        response["cascade"] = {

            "type":
                cascade_record["cascade_type"],

            "severity":
                cascade_record["severity"],

            "root_cause":
                cascade_record["root_cause"],

            "message":
                cascade_record["message"],

            "recommendation":
                cascade_record["recommendation"]
        }

    # ========================================================
    # RISK
    # ========================================================

    if not risk.empty:

        # Find same machine if available
        risk_machine = risk[
            risk["machine_id"] == machine_id
        ]

        if not risk_machine.empty:

            best_risk = risk_machine.iloc[0]

            response["risk"] = {

                "risk_score":
                    round(
                        float(
                            best_risk["risk_score"]
                        ),
                        2
                    ),

                "uncertainty_percent":
                    round(
                        float(
                            best_risk[
                                "energy_uncertainty_percent"
                            ]
                        ),
                        2
                    ),

                "robust_score":
                    round(
                        float(
                            best_risk["robust_score"]
                        ),
                        4
                    )
            }

    return response