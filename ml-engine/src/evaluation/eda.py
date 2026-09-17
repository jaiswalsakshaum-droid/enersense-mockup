import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

DATA_PATH = "data/raw/factory_production_data.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("ENNERSENSE — EXPLORATORY DATA ANALYSIS")
print("=" * 70)


# ---------------------------------------------------------
# Basic information
# ---------------------------------------------------------

print("\n1. DATASET SHAPE")
print("-" * 40)
print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]}")


print("\n2. COLUMNS")
print("-" * 40)

for column in df.columns:
    print(column)


# ---------------------------------------------------------
# Missing values
# ---------------------------------------------------------

print("\n3. MISSING VALUES")
print("-" * 40)

missing = df.isnull().sum()

print(missing[missing > 0])

if missing.sum() == 0:
    print("No missing values found.")


# ---------------------------------------------------------
# Duplicate rows
# ---------------------------------------------------------

print("\n4. DUPLICATES")
print("-" * 40)

print(f"Duplicate rows: {df.duplicated().sum():,}")


# ---------------------------------------------------------
# Machine distribution
# ---------------------------------------------------------

print("\n5. MACHINE DISTRIBUTION")
print("-" * 40)

print(df["machine_id"].value_counts())


# ---------------------------------------------------------
# Product distribution
# ---------------------------------------------------------

print("\n6. PRODUCT DISTRIBUTION")
print("-" * 40)

print(df["product_id"].value_counts())


# ---------------------------------------------------------
# Numerical statistics
# ---------------------------------------------------------

print("\n7. NUMERICAL STATISTICS")
print("-" * 40)

numeric_columns = [
    "load_percent",
    "speed_percent",
    "ambient_temperature_c",
    "machine_temperature_c",
    "maintenance_age_days",
    "cycle_time_sec",
    "production_qty",
    "energy_kwh",
    "downtime_min",
    "defect_rate",
    "electricity_price_inr_per_kwh",
    "energy_cost_inr",
    "co2_kg",
]

print(
    df[numeric_columns]
    .describe()
    .round(2)
)


# ---------------------------------------------------------
# Energy per unit
# ---------------------------------------------------------

df["energy_per_unit"] = (
    df["energy_kwh"]
    / df["production_qty"].replace(0, pd.NA)
)

print("\n8. ENERGY PER UNIT")
print("-" * 40)

print(
    df["energy_per_unit"]
    .describe()
    .round(3)
)


# ---------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------

print("\n9. CORRELATION WITH ENERGY")
print("-" * 40)

correlations = (
    df[numeric_columns]
    .corr()["energy_kwh"]
    .sort_values(ascending=False)
)

print(correlations.round(3))


# ---------------------------------------------------------
# Energy by machine
# ---------------------------------------------------------

print("\n10. ENERGY BY MACHINE")
print("-" * 40)

machine_energy = (
    df.groupby("machine_id")
    .agg(
        avg_energy_kwh=("energy_kwh", "mean"),
        avg_production=("production_qty", "mean"),
        avg_defect_rate=("defect_rate", "mean"),
        avg_load=("load_percent", "mean"),
    )
    .round(3)
)

print(machine_energy)


# ---------------------------------------------------------
# Energy by product
# ---------------------------------------------------------

print("\n11. ENERGY BY PRODUCT")
print("-" * 40)

product_energy = (
    df.groupby("product_id")
    .agg(
        avg_energy_kwh=("energy_kwh", "mean"),
        avg_production=("production_qty", "mean"),
        avg_defect_rate=("defect_rate", "mean"),
        avg_cycle_time=("cycle_time_sec", "mean"),
    )
    .round(3)
)

print(product_energy)


# ---------------------------------------------------------
# High-load analysis
# ---------------------------------------------------------

print("\n12. HIGH LOAD ANALYSIS")
print("-" * 40)

df["load_zone"] = pd.cut(
    df["load_percent"],
    bins=[0, 70, 82, 85, 90, 100],
    labels=[
        "Low",
        "Optimal",
        "Warning",
        "Inefficient",
        "Critical",
    ],
)

load_analysis = (
    df.groupby("load_zone", observed=True)
    .agg(
        avg_energy=("energy_kwh", "mean"),
        avg_energy_per_unit=("energy_per_unit", "mean"),
        avg_defect_rate=("defect_rate", "mean"),
        avg_production=("production_qty", "mean"),
        records=("load_percent", "size"),
    )
    .round(4)
)

print(load_analysis)


# ---------------------------------------------------------
# Plot 1 — Load vs Energy
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    df["load_percent"],
    df["energy_kwh"],
    alpha=0.15,
    s=8,
)

plt.xlabel("Machine Load (%)")
plt.ylabel("Energy Consumption (kWh)")
plt.title("Machine Load vs Energy Consumption")

plt.tight_layout()

plt.savefig(
    "data/load_vs_energy.png",
    dpi=150,
)

plt.close()


# ---------------------------------------------------------
# Plot 2 — Load vs Defect Rate
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    df["load_percent"],
    df["defect_rate"],
    alpha=0.15,
    s=8,
)

plt.xlabel("Machine Load (%)")
plt.ylabel("Defect Rate")
plt.title("Machine Load vs Defect Rate")

plt.tight_layout()

plt.savefig(
    "data/load_vs_defects.png",
    dpi=150,
)

plt.close()


# ---------------------------------------------------------
# Plot 3 — Energy by Machine
# ---------------------------------------------------------

machine_energy["avg_energy_kwh"].plot(
    kind="bar",
    figsize=(10, 6),
)

plt.xlabel("Machine")
plt.ylabel("Average Energy (kWh)")
plt.title("Average Energy Consumption by Machine")

plt.tight_layout()

plt.savefig(
    "data/energy_by_machine.png",
    dpi=150,
)

plt.close()


# ---------------------------------------------------------
# Plot 4 — Energy vs Production
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    df["production_qty"],
    df["energy_kwh"],
    alpha=0.15,
    s=8,
)

plt.xlabel("Production Quantity")
plt.ylabel("Energy Consumption (kWh)")
plt.title("Production Quantity vs Energy Consumption")

plt.tight_layout()

plt.savefig(
    "data/production_vs_energy.png",
    dpi=150,
)

plt.close()


print("\n" + "=" * 70)
print("EDA COMPLETE")
print("=" * 70)

print("\nGenerated plots:")
print("1. data/load_vs_energy.png")
print("2. data/load_vs_defects.png")
print("3. data/energy_by_machine.png")
print("4. data/production_vs_energy.png")