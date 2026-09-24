from datetime import datetime, timedelta
from app.database.connection import get_connection
from app.services.machine_health import get_machine_health
from app.services.production_calculations import (
    calculate_production_duration,
    calculate_energy,
    calculate_energy_cost,
    calculate_carbon,
    calculate_expected_defects,
    calculate_effective_quality,
    check_constraints,
)
def get_tariff(cur, factory_id, time_value):
    cur.execute("""
        SELECT
            price_per_kwh,
            carbon_factor_kg_per_kwh
        FROM energy_tariffs
        WHERE factory_id = %s
          AND start_time <= %s
          AND end_time >= %s
        ORDER BY price_per_kwh
        LIMIT 1;
    """, (factory_id, time_value, time_value))

    result = cur.fetchone()

    if result:
        return float(result[0]), float(result[1])

    # Fallback tariff
    return 7.20, 0.70

def simulate_order(order_id: str):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # --------------------------------
            # 1. GET ORDER
            # --------------------------------
            cur.execute("""
                SELECT
                    order_id,
                    factory_id,
                    product_id,
                    quantity,
                    deadline,
                    minimum_quality,
                    carbon_budget_kg
                FROM production_orders
                WHERE order_id = %s;
            """, (order_id,))

            order = cur.fetchone()

            if not order:
                return {
                    "error": "Production order not found"
                }

            (
                order_id,
                factory_id,
                product_id,
                quantity,
                deadline,
                minimum_quality,
                carbon_budget
            ) = order

            # --------------------------------
            # 2. FIND CAPABLE MACHINES
            # --------------------------------
            cur.execute("""
                SELECT
                    m.machine_id,
                    m.name,
                    m.capacity_units_per_hour,
                    m.quality_score,
                    c.energy_kwh_per_unit,
                    c.defect_rate
                FROM machines m
                JOIN machine_product_capabilities c
                    ON m.machine_id = c.machine_id
                WHERE c.product_id = %s
                AND m.factory_id = %s
                AND m.status = 'AVAILABLE';
            """, (product_id, factory_id))

            machines = cur.fetchall()

            if not machines:
                return {
                    "error": "No capable machines found"
                }

            # --------------------------------
            # 3. CHECK MACHINE HEALTH
            # --------------------------------
            eligible_machines = []
            critical_machines = []

            for machine in machines:
                machine_id = machine[0]
                health = get_machine_health(machine_id)

                # No telemetry means we cannot verify machine health.
                if health is None:
                    continue

                health_score = health["health_score"]
                health_status = health["health_status"]

                if health_status == "Critical":
                    critical_machines.append({
                        "machine_id": machine_id,
                        "name": machine[1],
                        "health_score": health_score,
                        "health_status": health_status,
                    })
                    continue

                eligible_machines.append(
                    machine + (health_score, health_status)
                )

            if not eligible_machines:
                return {
                    "error": "No healthy machines available for simulation",
                    "critical_machines": critical_machines,
                }

            # --------------------------------
            # 4. CREATE SIMULATION SCENARIOS
            # --------------------------------
            scenarios = []

            for machine in eligible_machines:
                (
                    machine_id,
                    machine_name,
                    capacity_per_hour,
                    quality_score,
                    energy_per_unit,
                    defect_rate,
                    health_score,
                    health_status,
                ) = machine

                capacity_per_hour = float(capacity_per_hour)
                quality_score = float(quality_score)
                energy_per_unit = float(energy_per_unit)
                defect_rate = float(defect_rate)
                health_score = int(health_score)

                # Production duration
                duration_hours = calculate_production_duration(
                    quantity,
                    capacity_per_hour,
                )

                start_time = datetime.now()

                completion_time = (
                    start_time +
                    timedelta(hours=duration_hours)
                )

                total_energy = calculate_energy(
                    quantity,
                    energy_per_unit,
                )

                tariff, carbon_factor = get_tariff(
                    cur,
                    factory_id,
                    start_time.time(),
                )

                total_cost = calculate_energy_cost(
                    total_energy,
                    tariff,
                )

                total_carbon = calculate_carbon(
                    total_energy,
                    carbon_factor,
                )

                expected_defects = calculate_expected_defects(
                    quantity,
                    defect_rate,
                )

                effective_quality = calculate_effective_quality(
                    quantity,
                    expected_defects,
                )

                constraint_result = check_constraints(
                    completion_time=completion_time,
                    deadline=deadline,
                    quality=effective_quality,
                    minimum_quality=minimum_quality,
                    carbon=total_carbon,
                    carbon_budget=carbon_budget,
                )

                deadline_met = constraint_result["deadline_met"]
                quality_met = constraint_result["quality_met"]
                carbon_met = constraint_result["carbon_budget_met"]
                feasible = constraint_result["feasible"]

                scenarios.append({
                    "machine_health": {
                        "score": health_score,
                        "status": health_status,
                    },
                    "energy_pricing": {
                        "price_per_kwh": tariff,
                        "carbon_factor_kg_per_kwh": carbon_factor,
                    },
                    "machine_id": machine_id,
                    "machine_name": machine_name,
                    "quantity": quantity,
                    "duration_hours": round(duration_hours, 2),
                    "start_time": start_time.isoformat(),
                    "completion_time": completion_time.isoformat(),
                    "energy_kwh": round(total_energy, 2),
                    "energy_cost_inr": round(total_cost, 2),
                    "carbon_kg": round(total_carbon, 2),
                    "expected_defects": expected_defects,
                    "quality_percent": round(effective_quality, 2),
                    "deadline_met": deadline_met,
                    "quality_met": quality_met,
                    "carbon_budget_met": carbon_met,
                    "feasible": feasible
                })

            # --------------------------------
            # 4. FIND BEST FEASIBLE SCENARIO
            # --------------------------------
            feasible_scenarios = [
                s for s in scenarios
                if s["feasible"]
            ]

            if feasible_scenarios:
                best = min(
                    feasible_scenarios,
                    key=lambda x: x["energy_cost_inr"]
                )

                recommendation = (
                    "Lowest-cost feasible production scenario"
                )
            else:
                best = None

                recommendation = (
                    "No single-machine scenario satisfies "
                    "all production constraints"
                )

            return {
                "order_id": order_id,
                "quantity": quantity,
                "deadline": deadline.isoformat(),
                "minimum_quality": float(minimum_quality),
                "energy_pricing": {
                    "price_per_kwh": (
                        scenarios[0]["energy_pricing"]["price_per_kwh"]
                        if scenarios
                        else 7.20
                    ),
                    "carbon_factor_kg_per_kwh": (
                        scenarios[0]["energy_pricing"]["carbon_factor_kg_per_kwh"]
                        if scenarios
                        else 0.70
                    ),
                },
                "critical_machines": critical_machines,
                "eligible_machines": [
                    {
                        "machine_id": machine[0],
                        "name": machine[1],
                        "health_score": machine[6],
                        "health_status": machine[7],
                    }
                    for machine in eligible_machines
                ],
                "carbon_budget_kg": (
                    float(carbon_budget)
                    if carbon_budget is not None
                    else None
                ),
                "scenarios": scenarios,
                "best_scenario": best,
                "recommendation": recommendation
            }

    finally:
        conn.close()
