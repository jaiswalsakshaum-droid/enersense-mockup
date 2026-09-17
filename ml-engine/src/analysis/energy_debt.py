import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SCENARIO_FILE = BASE_DIR / "data" / "feasible_scenarios.csv"
OUTPUT_FILE = BASE_DIR / "data" / "energy_debt_report.csv"

# A comparable scenario must produce at least 95%
# of the current scenario's production.
PRODUCTION_TOLERANCE = 0.05

# Allow a tiny quality tolerance of 0.1 percentage points.
QUALITY_TOLERANCE = 0.001


# ============================================================
# LOAD DATA
# ============================================================

def load_scenarios():
    """Load feasible operating scenarios."""

    df = pd.read_csv(SCENARIO_FILE)

    print(f"Loaded {len(df)} feasible scenarios")

    return df


# ============================================================
# FIND COMPARABLE SCENARIOS
# ============================================================

def find_comparable_scenarios(df, current_row):
    """
    Find scenarios that are comparable to the current operating state.

    Conditions:
    1. Same machine
    2. Same product
    3. Similar production output
    4. Similar or better quality
    """

    machine = current_row["machine_id"]
    product = current_row["product_id"]

    current_production = current_row["predicted_production_units"]
    current_defect = current_row["predicted_defect_rate"]

    min_production = current_production * (1 - PRODUCTION_TOLERANCE)

    comparable = df[
        (df["machine_id"] == machine)
        & (df["product_id"] == product)
        & (df["predicted_production_units"] >= min_production)
        & (
            df["predicted_defect_rate"]
            <= current_defect + QUALITY_TOLERANCE
        )
    ].copy()

    return comparable


# ============================================================
# CALCULATE ENERGY DEBT
# ============================================================

def calculate_energy_debt(df):
    """
    Calculate avoidable energy consumption for every scenario.

    Energy Debt:

        Current Energy
        -
        Best Comparable Energy

    The best comparable scenario is the lowest-energy scenario
    that achieves similar production and acceptable quality.
    """

    results = []

    for index, current_row in df.iterrows():

        comparable = find_comparable_scenarios(df, current_row)

        # If no comparable scenario exists
        if comparable.empty:
            results.append({
                "machine_id": current_row["machine_id"],
                "product_id": current_row["product_id"],
                "load_percent": current_row["load_percent"],
                "speed_percent": current_row["speed_percent"],
                "predicted_energy_kwh": current_row["predicted_energy_kwh"],
                "predicted_production_units": current_row[
                    "predicted_production_units"
                ],
                "predicted_defect_rate": current_row[
                    "predicted_defect_rate"
                ],
                "best_energy_kwh": np.nan,
                "energy_debt_kwh": np.nan,
                "energy_debt_percent": np.nan,
                "best_load_percent": np.nan,
                "best_speed_percent": np.nan,
                "status": "No comparable scenario"
            })

            continue

        # Find lowest-energy comparable scenario
        best = comparable.loc[
            comparable["predicted_energy_kwh"].idxmin()
        ]

        current_energy = current_row["predicted_energy_kwh"]
        best_energy = best["predicted_energy_kwh"]

        energy_debt = max(
            0,
            current_energy - best_energy
        )

        # Avoid division by zero
        if best_energy > 0:
            debt_percent = (
                energy_debt / best_energy
            ) * 100
        else:
            debt_percent = 0

        results.append({
            "machine_id": current_row["machine_id"],
            "product_id": current_row["product_id"],
            "load_percent": current_row["load_percent"],
            "speed_percent": current_row["speed_percent"],

            "predicted_energy_kwh": current_energy,

            "predicted_production_units": current_row[
                "predicted_production_units"
            ],

            "predicted_defect_rate": current_row[
                "predicted_defect_rate"
            ],

            "best_energy_kwh": best_energy,

            "energy_debt_kwh": energy_debt,

            "energy_debt_percent": debt_percent,

            "best_load_percent": best["load_percent"],

            "best_speed_percent": best["speed_percent"],

            "best_production_units": best[
                "predicted_production_units"
            ],

            "best_defect_rate": best[
                "predicted_defect_rate"
            ],

            "status": "Energy debt detected"
            if energy_debt > 0.01
            else "Near optimal"
        })

    return pd.DataFrame(results)


# ============================================================
# ADD COST IMPACT
# ============================================================

def calculate_cost_impact(result_df, scenario_df):
    """
    Estimate avoidable electricity cost.

    Electricity price is inferred from:

        predicted_energy_cost / predicted_energy

    because scenario_predictions contains predicted energy cost
    rather than the electricity price directly.
    """

    # Build price lookup from original scenario data
    price_df = scenario_df.copy()

    price_df["estimated_price_inr_per_kwh"] = (
        price_df["predicted_energy_cost_inr"]
        / price_df["predicted_energy_kwh"].replace(0, np.nan)
    )

    price_df = price_df[
        [
            "machine_id",
            "product_id",
            "load_percent",
            "speed_percent",
            "estimated_price_inr_per_kwh"
        ]
    ]

    result_df = result_df.merge(
        price_df,
        on=[
            "machine_id",
            "product_id",
            "load_percent",
            "speed_percent"
        ],
        how="left"
    )

    result_df["avoidable_cost_inr"] = (
        result_df["energy_debt_kwh"]
        * result_df["estimated_price_inr_per_kwh"]
    )

    return result_df


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("        ENNERSENSE ENERGY DEBT ENGINE")
    print("=" * 60)

    # Load scenarios
    df = load_scenarios()

    # Calculate debt
    result_df = calculate_energy_debt(df)

    # Add cost impact
    result_df = calculate_cost_impact(
        result_df,
        df
    )

    # Round numerical values
    numeric_columns = result_df.select_dtypes(
        include=[np.number]
    ).columns

    result_df[numeric_columns] = result_df[
        numeric_columns
    ].round(4)

    # Save report
    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    valid = result_df[
        result_df["energy_debt_kwh"].notna()
    ]

    debt_cases = valid[
        valid["energy_debt_kwh"] > 0.01
    ]

    print("\nEnergy Debt Analysis Complete")
    print("-" * 60)

    print(f"Total scenarios       : {len(result_df)}")
    print(f"Comparable scenarios  : {len(valid)}")
    print(f"Debt scenarios        : {len(debt_cases)}")

    if not debt_cases.empty:

        print(
            f"Average energy debt   : "
            f"{debt_cases['energy_debt_kwh'].mean():.2f} kWh"
        )

        print(
            f"Maximum energy debt   : "
            f"{debt_cases['energy_debt_kwh'].max():.2f} kWh"
        )

        print(
            f"Total avoidable cost  : "
            f"₹{debt_cases['avoidable_cost_inr'].sum():.2f}"
        )

        print("\nTop 10 Energy Debt Scenarios")
        print("-" * 60)

        top10 = debt_cases.sort_values(
            "energy_debt_kwh",
            ascending=False
        ).head(10)

        print(
            top10[
                [
                    "machine_id",
                    "product_id",
                    "load_percent",
                    "speed_percent",
                    "predicted_energy_kwh",
                    "best_energy_kwh",
                    "energy_debt_kwh",
                    "energy_debt_percent",
                    "avoidable_cost_inr",
                    "best_load_percent",
                    "best_speed_percent"
                ]
            ].to_string(index=False)
        )

    print("\nReport saved to:")
    print(OUTPUT_FILE)

    print("=" * 60)


if __name__ == "__main__":
    main()