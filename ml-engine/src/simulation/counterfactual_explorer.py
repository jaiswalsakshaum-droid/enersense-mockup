import pandas as pd
try:
    from src.simulation.simulate import predict_state
except ModuleNotFoundError:
    from simulate import predict_state


# =========================================================
# Counterfactual Factory Explorer
# =========================================================

def explore_counterfactuals(
    machine_id,
    product_id,

    current_load_percent,
    current_speed_percent,

    ambient_temperature_c,
    machine_temperature_c,
    maintenance_age_days,
    cycle_time_sec,
    shift,

    production_tolerance_percent=5,
    max_defect_rate=0.02
):

    # -----------------------------------------------------
    # 1. Predict current state
    # -----------------------------------------------------

    current = predict_state(
        machine_id,
        product_id,
        current_load_percent,
        current_speed_percent,
        ambient_temperature_c,
        machine_temperature_c,
        maintenance_age_days,
        cycle_time_sec,
        shift
    )

    current_production = current["production_units"]

    minimum_production = (
        current_production
        * (1 - production_tolerance_percent / 100)
    )

    # -----------------------------------------------------
    # 2. Generate counterfactual operating states
    # -----------------------------------------------------

    scenarios = []

    load_values = range(70, 101, 5)
    speed_values = range(70, 101, 5)

    for load in load_values:

        for speed in speed_values:

            prediction = predict_state(
                machine_id,
                product_id,
                load,
                speed,
                ambient_temperature_c,
                machine_temperature_c,
                maintenance_age_days,
                cycle_time_sec,
                shift
            )

            production = prediction["production_units"]
            defect = prediction["defect_rate"]
            energy = prediction["energy_kwh"]

            # -------------------------------------------------
            # Safety / feasibility constraints
            # -------------------------------------------------

            production_ok = (
                production >= minimum_production
            )

            quality_ok = (
                defect <= max_defect_rate
            )

            feasible = (
                production_ok
                and quality_ok
            )

            energy_saving = (
                current["energy_kwh"] - energy
            )

            energy_saving_percent = (
                energy_saving
                / current["energy_kwh"]
                * 100
                if current["energy_kwh"] > 0
                else 0
            )

            scenarios.append({

                "load_percent": load,

                "speed_percent": speed,

                "energy_kwh": energy,

                "production_units": production,

                "defect_rate": defect,

                "energy_per_unit":
                    prediction["energy_per_unit"],

                "energy_saving_kwh":
                    energy_saving,

                "energy_saving_percent":
                    energy_saving_percent,

                "production_change_percent":
                    (
                        (production - current_production)
                        / current_production
                        * 100
                    ),

                "feasible":
                    feasible,

                "production_ok":
                    production_ok,

                "quality_ok":
                    quality_ok
            })

    # -----------------------------------------------------
    # 3. Convert to DataFrame
    # -----------------------------------------------------

    df = pd.DataFrame(scenarios)

    # -----------------------------------------------------
    # 4. Keep feasible scenarios
    # -----------------------------------------------------

    feasible_df = df[
        df["feasible"] == True
    ].copy()

    # -----------------------------------------------------
    # 5. Rank by energy efficiency
    # -----------------------------------------------------

    feasible_df = feasible_df.sort_values(
        by="energy_per_unit",
        ascending=True
    )

    # -----------------------------------------------------
    # 6. Add rank
    # -----------------------------------------------------

    feasible_df["rank"] = range(
        1,
        len(feasible_df) + 1
    )

    # -----------------------------------------------------
    # 7. Return top alternatives
    # -----------------------------------------------------

    return {
        "current_state": current,

        "total_scenarios_tested":
            len(df),

        "feasible_scenarios":
            len(feasible_df),

        "minimum_required_production":
            minimum_production,

        "recommendations":
            feasible_df.head(10).to_dict(
                orient="records"
            )
    }


# =========================================================
# Local test
# =========================================================

if __name__ == "__main__":

    result = explore_counterfactuals(

        machine_id="HEAT_01",
        product_id="P001",

        current_load_percent=90,
        current_speed_percent=80,

        ambient_temperature_c=30,
        machine_temperature_c=70,
        maintenance_age_days=60,
        cycle_time_sec=60,
        shift="A"
    )

    print("\n============================================")
    print("     ENNERSENSE COUNTERFACTUAL EXPLORER")
    print("============================================")

    print(
        "\nCurrent state:"
    )

    print(
        result["current_state"]
    )

    print(
        "\nScenarios tested:",
        result["total_scenarios_tested"]
    )

    print(
        "Feasible scenarios:",
        result["feasible_scenarios"]
    )

    print(
        "\nTOP SAFE ENERGY-EFFICIENT OPTIONS"
    )

    for scenario in result["recommendations"]:

        print(
            f"\nRank {scenario['rank']}"
        )

        print(
            f"Load: {scenario['load_percent']}%"
        )

        print(
            f"Speed: {scenario['speed_percent']}%"
        )

        print(
            f"Energy: "
            f"{scenario['energy_kwh']:.2f} kWh"
        )

        print(
            f"Production: "
            f"{scenario['production_units']:.2f}"
        )

        print(
            f"Defect rate: "
            f"{scenario['defect_rate']:.4f}"
        )

        print(
            f"Energy/unit: "
            f"{scenario['energy_per_unit']:.4f}"
        )

        print(
            f"Energy saving: "
            f"{scenario['energy_saving_percent']:.2f}%"
        )