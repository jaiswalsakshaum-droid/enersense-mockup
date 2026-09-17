import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "energy_debt_report.csv"
OUTPUT_FILE = BASE_DIR / "data" / "energy_debt_summary.csv"


# ============================================================
# LOAD REPORT
# ============================================================

def load_energy_debt_report():

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df)} energy debt records")

    return df


# ============================================================
# CLASSIFY SEVERITY
# ============================================================

def classify_severity(debt_percent):

    if pd.isna(debt_percent):
        return "UNKNOWN"

    if debt_percent < 2:
        return "LOW"

    elif debt_percent < 5:
        return "MEDIUM"

    elif debt_percent < 10:
        return "HIGH"

    else:
        return "CRITICAL"


# ============================================================
# CREATE MACHINE SUMMARY
# ============================================================

def create_machine_summary(df):

    # Only consider records where a comparable scenario exists
    valid = df[
        df["energy_debt_kwh"].notna()
    ].copy()

    # Add severity
    valid["severity"] = valid[
        "energy_debt_percent"
    ].apply(classify_severity)

    # Aggregate by machine
    summary = (
        valid
        .groupby("machine_id")
        .agg(
            total_energy_debt_kwh=(
                "energy_debt_kwh",
                "sum"
            ),

            average_energy_debt_kwh=(
                "energy_debt_kwh",
                "mean"
            ),

            maximum_energy_debt_kwh=(
                "energy_debt_kwh",
                "max"
            ),

            average_energy_debt_percent=(
                "energy_debt_percent",
                "mean"
            ),

            maximum_energy_debt_percent=(
                "energy_debt_percent",
                "max"
            ),

            total_avoidable_cost_inr=(
                "avoidable_cost_inr",
                "sum"
            ),

            debt_cases=(
                "energy_debt_kwh",
                lambda x: (x > 0.01).sum()
            )
        )
        .reset_index()
    )

    # Number of critical/high cases
    severity_counts = (
        valid
        .groupby("machine_id")["severity"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )

    summary = summary.merge(
        severity_counts,
        on="machine_id",
        how="left"
    )

    # Overall machine severity
    summary["severity"] = (
        summary["maximum_energy_debt_percent"]
        .apply(classify_severity)
    )

    # Sort by total debt
    summary = summary.sort_values(
        "total_energy_debt_kwh",
        ascending=False
    )

    return summary


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 65)
    print("       ENNERSENSE ENERGY DEBT INTELLIGENCE")
    print("=" * 65)

    df = load_energy_debt_report()

    summary = create_machine_summary(df)

    # Round numbers
    numeric_columns = summary.select_dtypes(
        include="number"
    ).columns

    summary[numeric_columns] = summary[
        numeric_columns
    ].round(3)

    # Save
    summary.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print("\nMachine Energy Debt Summary")
    print("-" * 65)

    display_columns = [
        "machine_id",
        "total_energy_debt_kwh",
        "average_energy_debt_kwh",
        "maximum_energy_debt_kwh",
        "average_energy_debt_percent",
        "total_avoidable_cost_inr",
        "debt_cases",
        "severity"
    ]

    print(
        summary[
            display_columns
        ].to_string(index=False)
    )

    print("\n" + "-" * 65)

    total_debt = summary[
        "total_energy_debt_kwh"
    ].sum()

    total_cost = summary[
        "total_avoidable_cost_inr"
    ].sum()

    print(
        f"Total Energy Debt      : "
        f"{total_debt:.2f} kWh"
    )

    print(
        f"Potential Cost Saving  : "
        f"₹{total_cost:.2f}"
    )

    print("\nReport saved to:")

    print(OUTPUT_FILE)

    print("=" * 65)


if __name__ == "__main__":
    main()