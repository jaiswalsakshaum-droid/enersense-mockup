from datetime import datetime, timedelta
from app.database.connection import get_connection


def get_tariff(cur, time_value):
    cur.execute("""
        SELECT price_per_kwh, carbon_factor_kg_per_kwh
        FROM energy_tariffs
        WHERE factory_id = %s
        AND start_time <= %s
        AND end_time >= %s
        ORDER BY price_per_kwh
        LIMIT 1;
    """, ("FAC-001", time_value, time_value))

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
            # 3. CREATE SIMULATION SCENARIOS
            # --------------------------------
            scenarios = []

            for machine in machines:

                (
                    machine_id,
                    machine_name,
                    capacity_per_hour,
                    quality_score,
                    energy_per_unit,
                    defect_rate
                ) = machine

                capacity_per_hour = float(capacity_per_hour)
                quality_score = float(quality_score)
                energy_per_unit = float(energy_per_unit)
                defect_rate = float(defect_rate)

                # Production duration
                duration_hours = quantity / capacity_per_hour

                start_time = datetime.now()
                completion_time = start_time + timedelta(
                    hours=duration_hours
                )

                # Energy
                total_energy = quantity * energy_per_unit

                # Tariff
                tariff, carbon_factor = get_tariff(
                    cur,
                    start_time.time()
                )

                # Cost
                total_cost = total_energy * tariff

                # Carbon
                total_carbon = total_energy * carbon_factor

                # Expected defects
                expected_defects = round(
                    quantity * defect_rate
                )

                # Effective quality
                effective_quality = (
                    (quantity - expected_defects)
                    / quantity
                ) * 100

                # Deadline check
                deadline_met = completion_time <= deadline

                # Quality check
                quality_met = (
                    effective_quality >= minimum_quality
                )

                # Carbon check
                carbon_met = (
                    carbon_budget is None
                    or total_carbon <= float(carbon_budget)
                )

                feasible = (
                    deadline_met
                    and quality_met
                    and carbon_met
                )

                scenarios.append({
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