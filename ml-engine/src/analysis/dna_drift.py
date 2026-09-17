import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DNA_FILE = BASE_DIR / "data" / "process_dna.csv"

SCENARIO_FILE = BASE_DIR / "data" / "scenario_predictions.csv"

OUTPUT_FILE = BASE_DIR / "data" / "dna_drift_report.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    dna = pd.read_csv(DNA_FILE)

    scenarios = pd.read_csv(SCENARIO_FILE)

    print(f"Loaded {len(dna)} machine DNA profiles")
    print(f"Loaded {len(scenarios)} operating scenarios")

    return dna, scenarios


# ============================================================
# CALCULATE RANGE DEVIATION
# ============================================================

def calculate_deviation(value, minimum, maximum):
    """
    Returns deviation from the learned DNA range.

    0   = inside normal range
    > 0 = outside normal range
    """

    if minimum <= value <= maximum:
        return 0.0

    if value < minimum:
        return (minimum - value) / (maximum - minimum)

    return (value - maximum) / (maximum - minimum)


# ============================================================
# DRIFT DETECTION
# ============================================================

def detect_drift(dna, scenarios):

    results = []

    for _, scenario in scenarios.iterrows():

        machine_id = scenario["machine_id"]

        # Find DNA for this machine
        machine_dna = dna[
            dna["machine_id"] == machine_id
        ]

        if machine_dna.empty:
            continue

        machine_dna = machine_dna.iloc[0]

        # ----------------------------------------------------
        # Individual deviations
        # ----------------------------------------------------

        load_dev = calculate_deviation(
            scenario["load_percent"],
            machine_dna["load_min"],
            machine_dna["load_max"]
        )

        speed_dev = calculate_deviation(
            scenario["speed_percent"],
            machine_dna["speed_min"],
            machine_dna["speed_max"]
        )

        temp_dev = calculate_deviation(
            scenario["machine_temperature_c"],
            machine_dna["machine_temp_min"],
            machine_dna["machine_temp_max"]
        )

        energy_dev = calculate_deviation(
            scenario["predicted_energy_kwh"],
            machine_dna["energy_min"],
            machine_dna["energy_max"]
        )

        defect_dev = calculate_deviation(
            scenario["predicted_defect_rate"],
            0,
            machine_dna["defect_rate_max"]
        )

        # ----------------------------------------------------
        # Weighted drift score
        # ----------------------------------------------------

        weighted_drift = (
            load_dev * 0.20
            + speed_dev * 0.15
            + temp_dev * 0.20
            + energy_dev * 0.30
            + defect_dev * 0.15
        )

        drift_score = min(
            100,
            weighted_drift * 100
        )

        # ----------------------------------------------------
        # Severity
        # ----------------------------------------------------

        if drift_score < 10:
            severity = "NORMAL"

        elif drift_score < 25:
            severity = "WATCH"

        elif drift_score < 50:
            severity = "WARNING"

        else:
            severity = "CRITICAL"

        # ----------------------------------------------------
        # Find primary deviation
        # ----------------------------------------------------

        deviations = {
            "load": load_dev,
            "speed": speed_dev,
            "temperature": temp_dev,
            "energy": energy_dev,
            "quality": defect_dev
        }

        primary_issue = max(
            deviations,
            key=deviations.get
        )

        # ----------------------------------------------------
        # Explanation
        # ----------------------------------------------------

        explanations = {

            "load":
                "Operating load is outside the machine's normal process range.",

            "speed":
                "Operating speed is outside the machine's normal process range.",

            "temperature":
                "Machine temperature is outside the learned process range.",

            "energy":
                "Energy consumption is significantly different from the machine's normal operating fingerprint.",

            "quality":
                "Defect rate is outside the machine's normal quality envelope."
        }

        if severity == "NORMAL":
            explanation = (
                "Operating conditions are within the machine's "
                "learned process DNA."
            )

        elif severity == "WATCH":
            explanation = (
                f"Minor deviation detected in {primary_issue} "
                "from the machine's normal operating fingerprint."
            )

        elif severity == "WARNING":
            explanation = (
                f"Significant process drift detected in {primary_issue}. "
                "Inspect the operating conditions."
            )

        else:
            explanation = (
                f"Severe process drift detected in {primary_issue}. "
                "Immediate inspection is recommended."
            )

        results.append({

            "machine_id":
                machine_id,

            "product_id":
                scenario["product_id"],

            "load_percent":
                scenario["load_percent"],

            "speed_percent":
                scenario["speed_percent"],

            "machine_temperature_c":
                scenario["machine_temperature_c"],

            "predicted_energy_kwh":
                scenario["predicted_energy_kwh"],

            "predicted_defect_rate":
                scenario["predicted_defect_rate"],

            "load_deviation":
                load_dev,

            "speed_deviation":
                speed_dev,

            "temperature_deviation":
                temp_dev,

            "energy_deviation":
                energy_dev,

            "quality_deviation":
                defect_dev,

            "dna_drift_score":
                drift_score,

            "severity":
                severity,

            "primary_issue":
                primary_issue,

            "explanation":
                explanation
        })

    return pd.DataFrame(results)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("          ENNERSENSE PROCESS DNA DRIFT ENGINE")
    print("=" * 70)

    dna, scenarios = load_data()

    result = detect_drift(
        dna,
        scenarios
    )

    # Round numerical values
    numeric_columns = result.select_dtypes(
        include=np.number
    ).columns

    result[numeric_columns] = result[
        numeric_columns
    ].round(4)

    # Save
    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nDNA Drift Analysis Complete")
    print("-" * 70)

    print(
        result[
            [
                "machine_id",
                "load_percent",
                "speed_percent",
                "predicted_energy_kwh",
                "dna_drift_score",
                "severity",
                "primary_issue"
            ]
        ]
        .sort_values(
            "dna_drift_score",
            ascending=False
        )
        .head(15)
        .to_string(index=False)
    )

    print("\nReport saved to:")
    print(OUTPUT_FILE)

    print("=" * 70)


if __name__ == "__main__":
    main()