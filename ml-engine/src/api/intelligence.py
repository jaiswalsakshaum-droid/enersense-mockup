import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SCENARIO_FILE = BASE_DIR / "data" / "scenario_predictions.csv"

FEASIBLE_FILE = BASE_DIR / "data" / "feasible_scenarios.csv"

ENERGY_DEBT_FILE = BASE_DIR / "data" / "energy_debt_report.csv"

DNA_FILE = BASE_DIR / "data" / "dna_drift_report.csv"

CASCADE_FILE = BASE_DIR / "data" / "cascade_alerts.csv"

RISK_FILE = BASE_DIR / "data" / "risk_aware_recommendation.csv"


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

def find_closest_scenario(request, scenarios):

    # --------------------------------------------------------
    # Normalize IDs
    # --------------------------------------------------------

    scenarios["machine_id"] = scenarios["machine_id"].astype(str).str.strip()

    scenarios["product_id"] = scenarios["product_id"].astype(str).str.strip()

    machine_id = str(request["machine_id"]).strip()

    product_id = str(request["product_id"]).strip()

    # --------------------------------------------------------
    # First restrict to same machine + product
    # --------------------------------------------------------

    candidates = scenarios[
        (scenarios["machine_id"] == machine_id)
        &
        (scenarios["product_id"] == product_id)
    ].copy()

    if candidates.empty:
        return None

    # --------------------------------------------------------
    # Calculate distance
    # --------------------------------------------------------

    candidates["distance"] = (

        (
            candidates["load_percent"]
            - float(request["load_percent"])
        ).abs()

        +

        (
            candidates["speed_percent"]
            - float(request["speed_percent"])
        ).abs()

        +

        (
            candidates["machine_temperature_c"]
            - float(request["machine_temperature_c"])
        ).abs() * 0.5

        +

        (
            candidates["ambient_temperature_c"]
            - float(request["ambient_temperature_c"])
        ).abs() * 0.2

        +

        (
            candidates["maintenance_age_days"]
            - float(request["maintenance_age_days"])
        ).abs() * 0.1

        +

        (
            candidates["cycle_time_sec"]
            - float(request["cycle_time_sec"])
        ).abs() * 0.1
    )

    # --------------------------------------------------------
    # Return closest scenario
    # --------------------------------------------------------

    closest_index = candidates["distance"].idxmin()

    return candidates.loc[closest_index]


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
    # First filter by machine and product
    records = df[
        (df["machine_id"] == machine_id)
        & (df["product_id"] == product_id)
    ].copy()

    if records.empty:
        return None

    # Calculate distance based on load and speed
    records["distance"] = (
        (records["load_percent"] - load_percent).abs()
        +
        (records["speed_percent"] - speed_percent).abs()
    )

    # Return the closest available record
    closest = records.loc[
        records["distance"].idxmin()
    ]

    return closest

# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value, default=0.0):

    try:
        if pd.isna(value):
            return default

        return float(value)

    except (TypeError, ValueError):

        return default


# ============================================================
# BUILD INTELLIGENCE
# ============================================================

def get_intelligence(request):

    # --------------------------------------------------------
    # Load all reports
    # --------------------------------------------------------

    (
        scenarios,
        energy_debt,
        dna,
        cascade,
        risk,
    ) = load_reports()

    # --------------------------------------------------------
    # Find closest simulated scenario
    # --------------------------------------------------------

    scenario = find_closest_scenario(
        request,
        scenarios
    )

    if scenario is None:

        available_machines = sorted(
            scenarios["machine_id"]
            .astype(str)
            .unique()
            .tolist()
        )

        available_products = sorted(
            scenarios["product_id"]
            .astype(str)
            .unique()
            .tolist()
        )

        return {
            "status": "not_found",
            "message": (
                "No simulated scenario exists for "
                "this machine and product."
            ),
            "requested_machine": request["machine_id"],
            "requested_product": request["product_id"],
            "available_machines": available_machines,
            "available_products": available_products,
        }

    # --------------------------------------------------------
    # Extract operating state
    # --------------------------------------------------------

    machine_id = scenario["machine_id"]

    product_id = scenario["product_id"]

    load = scenario["load_percent"]

    speed = scenario["speed_percent"]

    # --------------------------------------------------------
    # Find supporting records
    # --------------------------------------------------------

    debt = find_record(
        energy_debt,
        machine_id,
        product_id,
        load,
        speed
    )

    dna_record = find_record(
        dna,
        machine_id,
        product_id,
        load,
        speed
    )

    cascade_record = find_record(
        cascade,
        machine_id,
        product_id,
        load,
        speed
    )

    # ========================================================
    # BASE RESPONSE
    # ========================================================

    response = {

        "status": "success",

        "machine_id": machine_id,

        "product_id": product_id,

        "operating_state": {

            "load_percent":
                safe_float(load),

            "speed_percent":
                safe_float(speed),

            "predicted_energy_kwh":
                round(
                    safe_float(
                        scenario["predicted_energy_kwh"]
                    ),
                    3
                ),

            "predicted_production_units":
                round(
                    safe_float(
                        scenario[
                            "predicted_production_units"
                        ]
                    ),
                    2
                ),

            "predicted_defect_rate":
                round(
                    safe_float(
                        scenario[
                            "predicted_defect_rate"
                        ]
                    ),
                    5
                ),

            "energy_per_unit":
                round(
                    safe_float(
                        scenario["energy_per_unit"]
                    ),
                    5
                ),

            "predicted_energy_cost_inr":
                round(
                    safe_float(
                        scenario["predicted_energy_cost_inr"]
                    ),
                    2
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
                    safe_float(
                        debt.get("energy_debt_kwh")
                    ),
                    3
                ),

            "energy_debt_percent":
                round(
                    safe_float(
                        debt.get("energy_debt_percent")
                    ),
                    2
                ),

            "avoidable_cost_inr":
                round(
                    safe_float(
                        debt.get("avoidable_cost_inr")
                    ),
                    2
                ),

            "best_load_percent":
                safe_float(
                    debt.get("best_load_percent")
                ),

            "best_speed_percent":
                safe_float(
                    debt.get("best_speed_percent")
                ),

            "status":
                str(
                    debt.get("status", "unknown")
                )
        }

    # ========================================================
    # PROCESS DNA
    # ========================================================

    if dna_record is not None:

        response["process_dna"] = {

            "drift_score":
                round(
                    safe_float(
                        dna_record.get(
                            "dna_drift_score"
                        )
                    ),
                    2
                ),

            "severity":
                str(
                    dna_record.get(
                        "severity",
                        "unknown"
                    )
                ),

            "primary_issue":
                str(
                    dna_record.get(
                        "primary_issue",
                        ""
                    )
                ),

            "explanation":
                str(
                    dna_record.get(
                        "explanation",
                        ""
                    )
                )
        }

    # ========================================================
    # CASCADE
    # ========================================================

    if cascade_record is not None:

        response["cascade"] = {

            "type":
                str(
                    cascade_record.get(
                        "cascade_type",
                        "unknown"
                    )
                ),

            "severity":
                str(
                    cascade_record.get(
                        "severity",
                        "unknown"
                    )
                ),

            "root_cause":
                str(
                    cascade_record.get(
                        "root_cause",
                        ""
                    )
                ),

            "message":
                str(
                    cascade_record.get(
                        "message",
                        ""
                    )
                ),

            "recommendation":
                str(
                    cascade_record.get(
                        "recommendation",
                        ""
                    )
                )
        }

    # ========================================================
    # RISK
    # ========================================================

    if not risk.empty and "machine_id" in risk.columns:

        risk_machine = risk[
            risk["machine_id"].astype(str).str.strip()
            == str(machine_id).strip()
        ]

        if not risk_machine.empty:

            best_risk = risk_machine.iloc[0]

            response["risk"] = {

                "risk_score":
                    round(
                        safe_float(
                            best_risk.get(
                                "risk_score"
                            )
                        ),
                        2
                    ),

                "uncertainty_percent":
                    round(
                        safe_float(
                            best_risk.get(
                                "energy_uncertainty_percent"
                            )
                        ),
                        2
                    ),

                "robust_score":
                    round(
                        safe_float(
                            best_risk.get(
                                "robust_score"
                            )
                        ),
                        4
                    )
            }

    return response