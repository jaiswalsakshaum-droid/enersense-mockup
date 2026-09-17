import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DNA_DRIFT_FILE = (
    BASE_DIR
    / "data"
    / "dna_drift_report.csv"
)

ENERGY_DEBT_FILE = (
    BASE_DIR
    / "data"
    / "energy_debt_report.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "cascade_alerts.csv"
)


# ============================================================
# THRESHOLDS
# ============================================================

DRIFT_THRESHOLD = 25

ENERGY_DEBT_THRESHOLD = 5

QUALITY_RISK_THRESHOLD = 0.01


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    dna = pd.read_csv(DNA_DRIFT_FILE)

    debt = pd.read_csv(ENERGY_DEBT_FILE)

    print(f"Loaded {len(dna)} DNA drift records")
    print(f"Loaded {len(debt)} energy debt records")

    return dna, debt


# ============================================================
# DETECT CASCADE
# ============================================================

def detect_cascade(dna, debt):

    # --------------------------------------------------------
    # Merge the two intelligence layers
    # --------------------------------------------------------

    keys = [
        "machine_id",
        "product_id",
        "load_percent",
        "speed_percent"
    ]

    merged = dna.merge(
        debt[
            keys
            + [
                "energy_debt_kwh",
                "energy_debt_percent",
                "avoidable_cost_inr"
            ]
        ],
        on=keys,
        how="left"
    )

    results = []

    for _, row in merged.iterrows():

        # ----------------------------------------------------
        # ENERGY SIGNAL
        # ----------------------------------------------------

        energy_signal = (
            row["energy_debt_kwh"] >=
            ENERGY_DEBT_THRESHOLD
        )

        # ----------------------------------------------------
        # PROCESS SIGNAL
        # ----------------------------------------------------

        process_signal = (
            row["dna_drift_score"] >=
            DRIFT_THRESHOLD
        )

        # ----------------------------------------------------
        # QUALITY SIGNAL
        # ----------------------------------------------------

        quality_signal = (
            row["predicted_defect_rate"] >=
            QUALITY_RISK_THRESHOLD
        )

        # ----------------------------------------------------
        # Count active signals
        # ----------------------------------------------------

        signal_count = sum([
            energy_signal,
            process_signal,
            quality_signal
        ])

        # ----------------------------------------------------
        # Cascade classification
        # ----------------------------------------------------

        if signal_count == 3:

            cascade_type = "FULL_CASCADE"

            severity = "CRITICAL"

            message = (
                "Energy inefficiency, process drift, "
                "and quality risk are occurring together."
            )

        elif energy_signal and process_signal:

            cascade_type = "ENERGY_PROCESS"

            severity = "HIGH"

            message = (
                "Elevated energy consumption is occurring "
                "alongside process DNA drift."
            )

        elif process_signal and quality_signal:

            cascade_type = "PROCESS_QUALITY"

            severity = "HIGH"

            message = (
                "Process DNA drift is accompanied by "
                "elevated quality risk."
            )

        elif energy_signal:

            cascade_type = "ENERGY_ONLY"

            severity = "MEDIUM"

            message = (
                "Energy consumption is above the "
                "recommended operating baseline."
            )

        elif process_signal:

            cascade_type = "PROCESS_ONLY"

            severity = "MEDIUM"

            message = (
                "Machine operating conditions are "
                "outside the learned process fingerprint."
            )

        elif quality_signal:

            cascade_type = "QUALITY_ONLY"

            severity = "MEDIUM"

            message = (
                "Predicted defect rate is above the "
                "quality risk threshold."
            )

        else:

            cascade_type = "NORMAL"

            severity = "NORMAL"

            message = (
                "No significant energy, process, "
                "or quality anomaly detected."
            )

        # ----------------------------------------------------
        # ROOT CAUSE
        # ----------------------------------------------------

        active_signals = {}

        if energy_signal:
            active_signals["energy"] = row["energy_deviation"]

        if process_signal:
            active_signals["process"] = (
                row["dna_drift_score"] / 100
            )

        if quality_signal:
            active_signals["quality"] = (
                row["quality_deviation"]
            )

        if active_signals:

            root_cause = max(
                active_signals,
                key=active_signals.get
            )

        else:

            root_cause = "none"

        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        if root_cause == "energy":

            recommendation = (
                "Evaluate the recommended lower-energy "
                "operating point before increasing production load."
            )

        elif root_cause == "process":

            recommendation = (
                "Inspect operating conditions against the "
                "machine's learned Process DNA."
            )

        elif root_cause == "quality":

            recommendation = (
                "Inspect quality-sensitive process parameters "
                "and maintenance condition."
            )

        else:

            recommendation = (
                "No immediate corrective action required."
            )

        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        results.append({

            "machine_id":
                row["machine_id"],

            "product_id":
                row["product_id"],

            "load_percent":
                row["load_percent"],

            "speed_percent":
                row["speed_percent"],

            "predicted_energy_kwh":
                row["predicted_energy_kwh"],

            "energy_debt_kwh":
                row["energy_debt_kwh"],

            "energy_debt_percent":
                row["energy_debt_percent"],

            "dna_drift_score":
                row["dna_drift_score"],

            "predicted_defect_rate":
                row["predicted_defect_rate"],

            "signal_count":
                signal_count,

            "cascade_type":
                cascade_type,

            "severity":
                severity,

            "root_cause":
                root_cause,

            "message":
                message,

            "recommendation":
                recommendation
        })

    return pd.DataFrame(results)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("        ENNERSENSE ENERGY → PROCESS → QUALITY CASCADE")
    print("=" * 70)

    dna, debt = load_data()

    result = detect_cascade(
        dna,
        debt
    )

    # Round numerical columns
    numeric_columns = result.select_dtypes(
        include=np.number
    ).columns

    result[numeric_columns] = result[
        numeric_columns
    ].round(4)

    # Sort critical situations first
    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "NORMAL": 3
    }

    result["_sort"] = result[
        "severity"
    ].map(severity_order)

    result = result.sort_values(
        "_sort"
    ).drop(
        columns="_sort"
    )

    # Save
    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\nCascade Analysis Complete")
    print("-" * 70)

    print(
        result[
            [
                "machine_id",
                "load_percent",
                "speed_percent",
                "energy_debt_kwh",
                "dna_drift_score",
                "predicted_defect_rate",
                "cascade_type",
                "severity",
                "root_cause"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print("\nCascade Counts")
    print("-" * 70)

    print(
        result["cascade_type"]
        .value_counts()
        .to_string()
    )

    print("\nReport saved to:")
    print(OUTPUT_FILE)

    print("=" * 70)


if __name__ == "__main__":
    main()