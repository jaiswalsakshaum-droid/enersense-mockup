import pandas as pd


# =========================================================
# Configuration
# =========================================================

INPUT_PATH = "data/feasible_scenarios.csv"

OUTPUT_PATH = "data/pareto_scenarios.csv"


# =========================================================
# Load feasible scenarios
# =========================================================

print("=" * 70)
print("ENNERSENSE — PARETO OPTIMIZATION")
print("=" * 70)

df = pd.read_csv(INPUT_PATH)

print(
    f"\nFeasible scenarios loaded: {len(df)}"
)


# =========================================================
# Pareto dominance
# =========================================================

def dominates(a, b):
    """
    Scenario A dominates scenario B if:

    - A uses <= energy
    - A has >= production
    - A has <= defect rate

    and A is strictly better in at least
    one of these objectives.
    """

    better_or_equal = (
        a["predicted_energy_kwh"]
        <= b["predicted_energy_kwh"]
        and
        a["predicted_production_units"]
        >= b["predicted_production_units"]
        and
        a["predicted_defect_rate"]
        <= b["predicted_defect_rate"]
    )

    strictly_better = (
        a["predicted_energy_kwh"]
        < b["predicted_energy_kwh"]
        or
        a["predicted_production_units"]
        > b["predicted_production_units"]
        or
        a["predicted_defect_rate"]
        < b["predicted_defect_rate"]
    )

    return better_or_equal and strictly_better


# =========================================================
# Find Pareto-optimal scenarios
# =========================================================

pareto_indices = []

records = df.to_dict("records")

for i, current in enumerate(records):

    dominated = False

    for j, other in enumerate(records):

        if i == j:
            continue

        if dominates(other, current):
            dominated = True
            break

    if not dominated:
        pareto_indices.append(i)


pareto_df = df.iloc[
    pareto_indices
].copy()


# =========================================================
# Calculate efficiency
# =========================================================

pareto_df["energy_per_unit"] = (
    pareto_df["predicted_energy_kwh"]
    /
    pareto_df["predicted_production_units"]
)


# =========================================================
# Sort
# =========================================================

pareto_df = pareto_df.sort_values(
    "predicted_energy_kwh"
)


# =========================================================
# Display results
# =========================================================

print("\n" + "=" * 70)
print("PARETO-OPTIMAL OPERATING PLANS")
print("=" * 70)

columns = [
    "load_percent",
    "speed_percent",
    "predicted_energy_kwh",
    "predicted_production_units",
    "predicted_defect_rate",
    "energy_per_unit",
]

display_df = pareto_df[columns].copy()

display_df["predicted_defect_rate"] *= 100

print(
    display_df.round(4).to_string(
        index=False
    )
)


# =========================================================
# Save
# =========================================================

pareto_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


print("\n" + "=" * 70)

print(
    f"Pareto scenarios found: {len(pareto_df)}"
)

print(
    f"Saved to: {OUTPUT_PATH}"
)

print("=" * 70)