import os
import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SEED = 42
NUM_RECORDS = 100_000

np.random.seed(SEED)


# ---------------------------------------------------------
# Factory configuration
# ---------------------------------------------------------

MACHINES = {
    "CNC_01": {
        "type": "CNC",
        "base_power_kw": 18,
        "max_load": 100,
        "efficiency": 0.92,
    },
    "CNC_02": {
        "type": "CNC",
        "base_power_kw": 21,
        "max_load": 100,
        "efficiency": 0.89,
    },
    "CNC_03": {
        "type": "CNC",
        "base_power_kw": 16,
        "max_load": 100,
        "efficiency": 0.94,
    },
    "PRESS_01": {
        "type": "PRESS",
        "base_power_kw": 35,
        "max_load": 100,
        "efficiency": 0.87,
    },
    "HEAT_01": {
        "type": "HEAT_TREATMENT",
        "base_power_kw": 50,
        "max_load": 100,
        "efficiency": 0.84,
    },
}


PRODUCTS = {
    "P001": {
        "name": "Brake Component",
        "base_cycle_time": 42,
        "complexity": 1.0,
    },
    "P002": {
        "name": "Housing Component",
        "base_cycle_time": 55,
        "complexity": 1.25,
    },
    "P003": {
        "name": "Shaft Component",
        "base_cycle_time": 35,
        "complexity": 0.9,
    },
}


# ---------------------------------------------------------
# Generate timestamps
# ---------------------------------------------------------

timestamps = pd.date_range(
    start="2025-01-01",
    periods=NUM_RECORDS,
    freq="15min",
)


# ---------------------------------------------------------
# Random factory conditions
# ---------------------------------------------------------

machine_ids = np.random.choice(
    list(MACHINES.keys()),
    size=NUM_RECORDS,
)

product_ids = np.random.choice(
    list(PRODUCTS.keys()),
    size=NUM_RECORDS,
)

df = pd.DataFrame({
    "timestamp": timestamps,
    "machine_id": machine_ids,
    "product_id": product_ids,
})


# ---------------------------------------------------------
# Shift
# ---------------------------------------------------------

hours = df["timestamp"].dt.hour

df["shift"] = np.select(
    [
        hours.between(6, 13),
        hours.between(14, 21),
    ],
    [
        "Morning",
        "Evening",
    ],
    default="Night",
)


# ---------------------------------------------------------
# Machine load
# ---------------------------------------------------------

df["load_percent"] = np.random.normal(
    loc=78,
    scale=12,
    size=NUM_RECORDS,
)

df["load_percent"] = np.clip(
    df["load_percent"],
    40,
    100,
)


# ---------------------------------------------------------
# Machine speed
# ---------------------------------------------------------

df["speed_percent"] = (
    df["load_percent"]
    + np.random.normal(0, 5, NUM_RECORDS)
)

df["speed_percent"] = np.clip(
    df["speed_percent"],
    40,
    105,
)


# ---------------------------------------------------------
# Ambient temperature
# ---------------------------------------------------------

df["ambient_temperature_c"] = np.random.normal(
    loc=27,
    scale=5,
    size=NUM_RECORDS,
)


# ---------------------------------------------------------
# Machine temperature
# ---------------------------------------------------------

df["machine_temperature_c"] = (
    42
    + 0.30 * df["load_percent"]
    + 0.10 * df["ambient_temperature_c"]
    + 0.015 * np.maximum(
        df["load_percent"] - 80,
        0,
    ) ** 2
    + np.random.normal(0, 2.5, NUM_RECORDS)
)

# ---------------------------------------------------------
# Maintenance age
# ---------------------------------------------------------

df["maintenance_age_days"] = np.random.randint(
    0,
    120,
    NUM_RECORDS,
)


# ---------------------------------------------------------
# Cycle time
# ---------------------------------------------------------

complexity = df["product_id"].map(
    lambda x: PRODUCTS[x]["complexity"]
)

base_cycle_time = df["product_id"].map(
    lambda x: PRODUCTS[x]["base_cycle_time"]
)

df["cycle_time_sec"] = (
    base_cycle_time
    * complexity
    * (1 + (100 - df["load_percent"]) / 500)
    + np.random.normal(0, 2, NUM_RECORDS)
)


# ---------------------------------------------------------
# Production quantity
# ---------------------------------------------------------

# Production increases with load and speed,
# but approaches machine/process capacity.

load_factor = df["load_percent"] / 100
speed_factor = df["speed_percent"] / 100

# Base production capacity
base_capacity = 650

df["production_qty"] = (
    base_capacity
    * load_factor
    * speed_factor
    / complexity
)

# Add realistic production variability
df["production_qty"] += np.random.normal(
    0,
    20,
    NUM_RECORDS,
)

# Production cannot be negative
df["production_qty"] = np.maximum(
    df["production_qty"],
    1,
)


# ---------------------------------------------------------
# Energy consumption
# ---------------------------------------------------------

machine_power = df["machine_id"].map(
    lambda x: MACHINES[x]["base_power_kw"]
)

machine_efficiency = df["machine_id"].map(
    lambda x: MACHINES[x]["efficiency"]
)


# Normal energy behaviour
energy = (
    machine_power
    * (0.35 + 0.65 * (df["load_percent"] / 100))
    / machine_efficiency
)


# Strong nonlinear energy penalty above the
# efficient operating region.

high_load_penalty = np.where(
    df["load_percent"] > 82,
    ((df["load_percent"] - 82) ** 2) * 0.25,
    0,
)

energy += high_load_penalty


# Maintenance deterioration
energy *= (
    1
    + df["maintenance_age_days"] * 0.0015
)


# Temperature effect
energy *= (
    1
    + np.maximum(
        df["machine_temperature_c"] - 70,
        0,
    ) * 0.003
)


# Random noise
energy += np.random.normal(
    0,
    1.5,
    NUM_RECORDS,
)

df["energy_kwh"] = np.maximum(
    energy,
    0.5,
)


# ---------------------------------------------------------
# Downtime
# ---------------------------------------------------------

downtime_probability = (
    0.02
    + 0.0015 * df["maintenance_age_days"]
    + 0.0008 * np.maximum(
        df["load_percent"] - 85,
        0,
    )
)

downtime_probability = np.clip(
    downtime_probability,
    0,
    0.5,
)

is_downtime = (
    np.random.random(NUM_RECORDS)
    < downtime_probability
)

df["downtime_min"] = np.where(
    is_downtime,
    np.random.uniform(5, 60, NUM_RECORDS),
    0,
)


# ---------------------------------------------------------
# Defect rate
# ---------------------------------------------------------

defect_rate = (
    0.005
    + 0.00025
    * np.maximum(
        df["load_percent"] - 82,
        0,
    ) ** 1.5
    + 0.00015
    * np.maximum(
        df["machine_temperature_c"] - 72,
        0,
    )
    + 0.00008
    * df["maintenance_age_days"]
)

defect_rate += np.random.normal(
    0,
    0.002,
    NUM_RECORDS,
)

df["defect_rate"] = np.clip(
    defect_rate,
    0,
    0.30,
)


# ---------------------------------------------------------
# Electricity tariff
# ---------------------------------------------------------

df["electricity_price_inr_per_kwh"] = np.select(
    [
        df["shift"] == "Morning",
        df["shift"] == "Evening",
        df["shift"] == "Night",
    ],
    [
        8.5,
        11.5,
        6.0,
    ],
)


# ---------------------------------------------------------
# Energy cost
# ---------------------------------------------------------

df["energy_cost_inr"] = (
    df["energy_kwh"]
    * df["electricity_price_inr_per_kwh"]
)


# ---------------------------------------------------------
# CO2 emissions
# ---------------------------------------------------------

GRID_EMISSION_FACTOR = 0.70

df["co2_kg"] = (
    df["energy_kwh"]
    * GRID_EMISSION_FACTOR
)


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

output_dir = "data/raw"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(
    output_dir,
    "factory_production_data.csv",
)

df.to_csv(
    output_path,
    index=False,
)

print("=" * 60)
print("EnnerSense Factory Dataset Generated")
print("=" * 60)
print(f"Records: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path}")
print()
print(df.head())
print()
print(df.describe())