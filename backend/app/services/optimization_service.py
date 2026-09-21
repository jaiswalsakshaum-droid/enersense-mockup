from datetime import datetime, timedelta

from app.database.connection import get_connection
from app.services.machine_health import get_machine_health


def get_current_tariff(cur, factory_id: str, timestamp: datetime):
    current_time = timestamp.time()

    cur.execute("""
        SELECT
            price_per_kwh,
            carbon_factor_kg_per_kwh
        FROM energy_tariffs
        WHERE factory_id = %s
          AND start_time <= %s
          AND end_time >= %s
        ORDER BY start_time DESC
        LIMIT 1;
    """, (factory_id, current_time, current_time))

    row = cur.fetchone()

    if row:
        return float(row[0]), float(row[1])

    # Fallback if no tariff is configured for the current time.
    return 7.20, 0.70

def optimize_order(order_id: str):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # 1. Get production order
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

            # 2. Find machines capable of producing the product
            cur.execute("""
                SELECT
                    m.machine_id,
                    m.name,
                    m.capacity_units_per_hour,
                    c.energy_kwh_per_unit,
                    c.defect_rate
                FROM machines m
                JOIN machine_product_capabilities c
                    ON m.machine_id = c.machine_id
                WHERE m.factory_id = %s
                  AND c.product_id = %s
                  AND m.status = 'AVAILABLE';
            """, (factory_id, product_id))

            machines = cur.fetchall()

            if not machines:
                return {
                    "error": "No capable machines found"
                }

            # 3. Check current health of each capable machine
            healthy_machines = []
            critical_machines = []

            for machine in machines:

                machine_id = machine[0]

                health = get_machine_health(machine_id)

                # If no telemetry is available, do not use the machine
                # for a health-aware production plan.
                if health is None:
                    continue

                machine_health_score = health["health_score"]
                machine_health_status = health["health_status"]

                # Critical machines are excluded from new production plans.
                if machine_health_status == "Critical":

                    critical_machines.append({
                        "machine_id": machine_id,
                        "name": machine[1],
                        "health_score": machine_health_score,
                        "health_status": machine_health_status,
                    })

                    continue

                # Keep the original machine data and append health information.
                healthy_machines.append(
                    machine + (
                        machine_health_score,
                        machine_health_status,
                    )
                )

            # If every capable machine is either unhealthy or has no telemetry,
            # no health-aware production plan can be created.
            if not healthy_machines:
                return {
                    "error": "No healthy machines available for production",
                    "critical_machines": critical_machines,
                }

            # 4. Start simulation
            start_time = datetime.now()

            scenarios = []

            # We currently optimize using the first two healthy capable machines.
            selected_machines = healthy_machines[:2]

            # ---------------------------------------------------------
            # SINGLE MACHINE SCENARIO
            # ---------------------------------------------------------

            if len(selected_machines) == 1:

                machine = selected_machines[0]

                machine_id = machine[0]
                machine_name = machine[1]
                capacity = float(machine[2])
                energy_per_unit = float(machine[3])
                defect_rate = float(machine[4])
                health_score = machine[5]
                health_status = machine[6]

                duration = quantity / capacity

                completion = (
                    start_time +
                    timedelta(hours=duration)
                )

                energy = quantity * energy_per_unit

                tariff, carbon_factor = get_current_tariff(
                      cur,
                      factory_id,
                      start_time
                )

                cost = energy * tariff
                carbon = energy * carbon_factor

                quality = 100 - (defect_rate * 100)

                deadline_met = completion <= deadline

                quality_met = quality >= float(minimum_quality)

                carbon_budget_met = (
                    carbon_budget is None
                    or carbon <= float(carbon_budget)
                )

                feasible = (
                    deadline_met
                    and quality_met
                    and carbon_budget_met
                )

                scenarios.append({
                    "allocation": {
                        machine_id: quantity
                    },
                    "machine_names": {
                        machine_id: machine_name
                    },
                    "machine_health": {
                        machine_id: {
                            "score": health_score,
                            "status": health_status,
                        }
                    },
                    "energy_kwh": round(energy, 2),
                    "cost_inr": round(cost, 2),
                    "carbon_kg": round(carbon, 2),
                    "duration_hours": round(duration, 2),
                    "completion_time": completion.isoformat(),
                    "quality_percent": round(quality, 2),
                    "deadline_met": deadline_met,
                    "quality_met": quality_met,
                    "carbon_budget_met": carbon_budget_met,
                    "feasible": feasible,
                })

            # ---------------------------------------------------------
            # TWO MACHINE SCENARIO
            # ---------------------------------------------------------

            else:

                m1 = selected_machines[0]
                m2 = selected_machines[1]

                # Machine 1
                m1_id = m1[0]
                m1_name = m1[1]
                m1_capacity = float(m1[2])
                m1_energy = float(m1[3])
                m1_defect = float(m1[4])
                m1_health_score = m1[5]
                m1_health_status = m1[6]

                # Machine 2
                m2_id = m2[0]
                m2_name = m2[1]
                m2_capacity = float(m2[2])
                m2_energy = float(m2[3])
                m2_defect = float(m2[4])
                m2_health_score = m2[5]
                m2_health_status = m2[6]

                # Test allocations every 500 units
                step = 500

                for qty1 in range(0, quantity + 1, step):

                    qty2 = quantity - qty1

                    time1 = (
                        qty1 / m1_capacity
                        if qty1 > 0
                        else 0
                    )

                    time2 = (
                        qty2 / m2_capacity
                        if qty2 > 0
                        else 0
                    )

                    # Both machines work in parallel
                    duration = max(time1, time2)

                    completion = (
                        start_time +
                        timedelta(hours=duration)
                    )

                    energy = (
                        qty1 * m1_energy +
                        qty2 * m2_energy
                    )

                    defects = (
                        qty1 * m1_defect +
                        qty2 * m2_defect
                    )

                    quality = (
                        100 -
                        (defects / quantity * 100)
                    )
                    tariff, carbon_factor = get_current_tariff(
                            cur,
                            factory_id,
                            start_time
                    )

                    cost = energy * tariff
                    carbon = energy * carbon_factor
                    

                    deadline_met = (
                        completion <= deadline
                    )

                    quality_met = (
                        quality >= float(minimum_quality)
                    )

                    carbon_budget_met = (
                        carbon_budget is None
                        or carbon <= float(carbon_budget)
                    )

                    feasible = (
                        deadline_met
                        and quality_met
                        and carbon_budget_met
                    )

                    scenarios.append({
                        "allocation": {
                            m1_id: qty1,
                            m2_id: qty2
                        },
                        "machine_names": {
                            m1_id: m1_name,
                            m2_id: m2_name
                        },
                        "machine_health": {
                            m1_id: {
                                "score": m1_health_score,
                                "status": m1_health_status,
                            },
                            m2_id: {
                                "score": m2_health_score,
                                "status": m2_health_status,
                            }
                        },
                        "energy_kwh": round(energy, 2),
                        "cost_inr": round(cost, 2),
                        "carbon_kg": round(carbon, 2),
                        "duration_hours": round(
                            duration, 2
                        ),
                        "completion_time": (
                            completion.isoformat()
                        ),
                        "quality_percent": round(
                            quality, 2
                        ),
                        "deadline_met": deadline_met,
                        "quality_met": quality_met,
                        "carbon_budget_met": carbon_budget_met,
                        "feasible": feasible
                    })

            # 5. Find feasible plans
            feasible_plans = [
                scenario
                for scenario in scenarios
                if (
                    scenario.get("deadline_met")
                    and scenario.get("quality_met")
                    and scenario.get("carbon_budget_met")
                )
            ]

            # 6. Select lowest-cost feasible plan
            if feasible_plans:

                best_plan = min(
                    feasible_plans,
                    key=lambda x: x["cost_inr"]
                )

                message = (
                    "Lowest-cost feasible production "
                    "allocation found."
                )

            else:

                best_plan = None

                message = (
                    "No feasible production allocation "
                    "was found for the current constraints."
                )

            # 7. Baseline:
            # Produce the entire order on the first selected machine.
            baseline = None

            if selected_machines:

                baseline_machine_id = selected_machines[0][0]

                baseline_candidates = [
                    scenario
                    for scenario in scenarios
                    if (
                        scenario["allocation"].get(
                            baseline_machine_id,
                            0
                        ) == quantity
                        and sum(
                            scenario["allocation"].values()
                        ) == quantity
                    )
                ]

                if baseline_candidates:
                    baseline = baseline_candidates[0]

            # 8. Return optimization result
            return {
                "order_id": order_id,
                "quantity": quantity,
                "deadline": deadline.isoformat(),
                "minimum_quality": float(minimum_quality),
                "total_scenarios_tested": len(scenarios),
                "critical_machines": critical_machines,
                "eligible_machines": [
                    {
                        "machine_id": machine[0],
                        "name": machine[1],
                        "health_score": machine[5],
                        "health_status": machine[6],
                    }
                    for machine in selected_machines
                ],
                "baseline": baseline,
                "best_plan": best_plan,
                "message": message
            }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:
        conn.close()