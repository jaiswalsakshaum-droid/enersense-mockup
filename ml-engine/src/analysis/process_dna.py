import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "factory_production_data.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "process_dna.csv"
)


# ============================================================
# HEALTHY OPERATING PERCENTILE RANGE
# ============================================================

LOW_PERCENTILE = 10
HIGH_PERCENTILE = 90


# ============================================================
# LOAD DATA
# ============================================================

def load_factory_data():

    df = pd.read_csv(DATA_FILE)

    print(f"Loaded {len(df)} factory records")

    return df


# ============================================================
# CREATE MACHINE DNA
# ============================================================

def build_process_dna(df):

    machines = []

    grouped = df.groupby("machine_id")

    for machine_id, machine_df in grouped:

        dna = {
            "machine_id": machine_id,

            # ------------------------------------------------
            # LOAD
            # ------------------------------------------------

            "load_min": np.percentile(
                machine_df["load_percent"],
                LOW_PERCENTILE
            ),

            "load_max": np.percentile(
                machine_df["load_percent"],
                HIGH_PERCENTILE
            ),

            "load_mean": machine_df[
                "load_percent"
            ].mean(),

            # ------------------------------------------------
            # SPEED
            # ------------------------------------------------

            "speed_min": np.percentile(
                machine_df["speed_percent"],
                LOW_PERCENTILE
            ),

            "speed_max": np.percentile(
                machine_df["speed_percent"],
                HIGH_PERCENTILE
            ),

            "speed_mean": machine_df[
                "speed_percent"
            ].mean(),

            # ------------------------------------------------
            # TEMPERATURE
            # ------------------------------------------------

            "machine_temp_min": np.percentile(
                machine_df["machine_temperature_c"],
                LOW_PERCENTILE
            ),

            "machine_temp_max": np.percentile(
                machine_df["machine_temperature_c"],
                HIGH_PERCENTILE
            ),

            "machine_temp_mean": machine_df[
                "machine_temperature_c"
            ].mean(),

            # ------------------------------------------------
            # ENERGY
            # ------------------------------------------------

            "energy_min": np.percentile(
                machine_df["energy_kwh"],
                LOW_PERCENTILE
            ),

            "energy_max": np.percentile(
                machine_df["energy_kwh"],
                HIGH_PERCENTILE
            ),

            "energy_mean": machine_df[
                "energy_kwh"
            ].mean(),

            # ------------------------------------------------
            # PRODUCTION
            # ------------------------------------------------

            "production_mean": machine_df[
                "production_qty"
            ].mean(),

            # ------------------------------------------------
            # QUALITY
            # ------------------------------------------------

            "defect_rate_mean": machine_df[
                "defect_rate"
            ].mean(),

            "defect_rate_max": np.percentile(
                machine_df["defect_rate"],
                HIGH_PERCENTILE
            ),

            # ------------------------------------------------
            # MAINTENANCE
            # ------------------------------------------------

            "maintenance_age_mean": machine_df[
                "maintenance_age_days"
            ].mean(),

            # Number of observations
            "observations": len(machine_df)
        }

        machines.append(dna)

    return pd.DataFrame(machines)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 65)
    print("          ENNERSENSE PROCESS DNA ENGINE")
    print("=" * 65)

    df = load_factory_data()

    dna = build_process_dna(df)

    # Round values
    numeric_columns = dna.select_dtypes(
        include="number"
    ).columns

    dna[numeric_columns] = dna[
        numeric_columns
    ].round(3)

    # Save
    dna.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nProcess DNA created")
    print("-" * 65)

    print(
        dna.to_string(index=False)
    )

    print("\nSaved to:")

    print(OUTPUT_FILE)

    print("=" * 65)


if __name__ == "__main__":
    main()