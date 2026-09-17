import pandas as pd


# =========================================================
# Configuration
# =========================================================

SCENARIO_PATH = "data/scenario_predictions.csv"


# Factory operating constraints
MIN_PRODUCTION = 450

MAX_DEFECT_RATE = 0.015

MAX_MACHINE_TEMPERATURE = 80

MAX_LOAD = 90


# =========================================================
# Load scenarios
# =========================================================

print("=" * 70)
print("ENNERSENSE — OPERATING OPTIMIZATION ENGINE")
print("=" * 70)

scenarios = pd.read_csv(
    SCENARIO_PATH
)

print(
    f"\nTotal scenarios evaluated: {len(scenarios)}"
)


# =========================================================
# Apply constraints
# =========================================================

print("\nApplying factory constraints...")

feasible = scenarios[
    (scenarios["predicted_production_units"] >= MIN_PRODUCTION)
    &
    (scenarios["predicted_defect_rate"] <= MAX_DEFECT_RATE)
    &
    (scenarios["machine_temperature_c"] <= MAX_MACHINE_TEMPERATURE)
    &
    (scenarios["load_percent"] <= MAX_LOAD)
].copy()


# =========================================================
# Feasibility summary
# =========================================================

print(
    f"Feasible scenarios: {len(feasible)}"
)

print(
    f"Infeasible scenarios: "
    f"{len(scenarios) - len(feasible)}"
)


# =========================================================
# Check if feasible solutions exist
# =========================================================

if feasible.empty:

    print("\nNo feasible operating scenario found.")

    print(
        "\nTry relaxing one of the factory constraints."
    )

    raise SystemExit


# =========================================================
# Calculate energy efficiency
# =========================================================

feasible["energy_per_unit"] = (
    feasible["predicted_energy_kwh"]
    / feasible["predicted_production_units"]
)


# =========================================================
# Rank feasible scenarios
# =========================================================

feasible = feasible.sort_values(
    "energy_per_unit"
)


# =========================================================
# Best energy-efficient scenario
# =========================================================

best = feasible.iloc[0]


# =========================================================
# Print recommendation
# =========================================================

print("\n" + "=" * 70)
print("ENNERSENSE RECOMMENDED OPERATING PLAN")
print("=" * 70)

print(
    f"\nMachine: {best['machine_id']}"
)

print(
    f"Product: {best['product_id']}"
)

print(
    f"Recommended Load: "
    f"{best['load_percent']:.0f}%"
)

print(
    f"Recommended Speed: "
    f"{best['speed_percent']:.0f}%"
)

print("\nPredicted performance:")
print("-" * 40)

print(
    f"Energy consumption : "
    f"{best['predicted_energy_kwh']:.2f} kWh"
)

print(
    f"Production output  : "
    f"{best['predicted_production_units']:.2f} units"
)

print(
    f"Defect rate        : "
    f"{best['predicted_defect_rate'] * 100:.2f}%"
)

print(
    f"Energy / unit      : "
    f"{best['energy_per_unit']:.4f} kWh/unit"
)

print(
    f"Energy cost        : "
    f"₹{best['predicted_energy_cost_inr']:.2f}"
)


# =========================================================
# Show top feasible scenarios
# =========================================================

print("\n" + "=" * 70)
print("TOP 10 FEASIBLE OPERATING SCENARIOS")
print("=" * 70)

columns = [
    "load_percent",
    "speed_percent",
    "predicted_energy_kwh",
    "predicted_production_units",
    "predicted_defect_rate",
    "energy_per_unit",
    "predicted_energy_cost_inr",
]

display_data = feasible[
    columns
].head(10).copy()

display_data["predicted_defect_rate"] *= 100

print(
    display_data.round(4).to_string(
        index=False
    )
)


# =========================================================
# Save recommendation
# =========================================================

best.to_frame().T.to_csv(
    "data/recommended_operating_plan.csv",
    index=False,
)

feasible.to_csv(
    "data/feasible_scenarios.csv",
    index=False,
)


print("\nRecommendation saved to:")

print(
    "data/recommended_operating_plan.csv"
)

print("\nFeasible scenarios saved to:")

print(
    "data/feasible_scenarios.csv"
)


print("\n" + "=" * 70)
print("OPTIMIZATION COMPLETE")
print("=" * 70)