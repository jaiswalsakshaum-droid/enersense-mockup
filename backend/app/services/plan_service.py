from datetime import datetime, timedelta

from app.database.connection import get_connection


def save_optimized_plan(order_id: str, best_plan: dict):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Get order information
            cur.execute("""
                SELECT
                    factory_id,
                    product_id,
                    quantity
                FROM production_orders
                WHERE order_id = %s;
            """, (order_id,))

            order = cur.fetchone()

            if not order:
                raise ValueError("Production order not found")

            factory_id, product_id, quantity = order

            # Generate unique plan ID
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            plan_id = f"PLAN-{timestamp}"

            # Values from optimizer
            total_energy = best_plan["energy_kwh"]
            total_cost = best_plan["cost_inr"]
            total_carbon = best_plan["carbon_kg"]
            quality = best_plan["quality_percent"]

            completion_time = datetime.fromisoformat(
                best_plan["completion_time"]
            )

            # Calculate peak demand
            peak_demand = 0

            for machine_id, allocated_quantity in best_plan[
                "allocation"
            ].items():

                if allocated_quantity <= 0:
                    continue

                cur.execute("""
                    SELECT
                        baseline_power_kw
                    FROM machines
                    WHERE machine_id = %s;
                """, (machine_id,))

                result = cur.fetchone()

                if result:
                    peak_demand += float(result[0])

            # Save production plan
            cur.execute("""
                INSERT INTO production_plans
                (
                    plan_id,
                    order_id,
                    status,
                    total_cost_inr,
                    total_energy_kwh,
                    total_carbon_kg,
                    completion_time,
                    quality_percent,
                    peak_demand_kw
                )
                VALUES
                (%s, %s, 'OPTIMIZED', %s, %s, %s, %s, %s, %s);
            """, (
                plan_id,
                order_id,
                total_cost,
                total_energy,
                total_carbon,
                completion_time,
                quality,
                peak_demand
            ))

            # --------------------------------
            # Save individual operations
            # --------------------------------

            duration_hours = best_plan["duration_hours"]

            start_time = (
                completion_time -
                timedelta(hours=duration_hours)
            )

            for machine_id, allocated_quantity in best_plan[
                "allocation"
            ].items():

                if allocated_quantity <= 0:
                    continue

                cur.execute("""
                    SELECT
                        c.energy_kwh_per_unit,
                        c.defect_rate,
                        m.capacity_units_per_hour
                    FROM machine_product_capabilities c
                    JOIN machines m
                        ON m.machine_id = c.machine_id
                    WHERE c.machine_id = %s
                    AND c.product_id = %s;
                """, (
                    machine_id,
                    product_id
                ))

                machine_data = cur.fetchone()

                if not machine_data:
                    continue

                energy_per_unit = float(machine_data[0])
                defect_rate = float(machine_data[1])
                capacity = float(machine_data[2])

                duration = (
                    allocated_quantity /
                    capacity
                )

                operation_end = (
                    start_time +
                    timedelta(hours=duration)
                )

                energy = (
                    allocated_quantity *
                    energy_per_unit
                )

                expected_defects = round(
                    allocated_quantity *
                    defect_rate
                )

                # Save operation
                cur.execute("""
                    INSERT INTO plan_operations
                    (
                        plan_id,
                        machine_id,
                        product_id,
                        quantity,
                        start_time,
                        end_time,
                        energy_kwh,
                        cost_inr,
                        carbon_kg,
                        expected_defects
                    )
                    VALUES
                    (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    );
                """, (
                    plan_id,
                    machine_id,
                    product_id,
                    allocated_quantity,
                    start_time,
                    operation_end,
                    energy,
                    0,
                    0,
                    expected_defects
                ))

            conn.commit()

            return {
                "plan_id": plan_id,
                "order_id": order_id,
                "status": "OPTIMIZED",
                "message": (
                    "Optimized production plan "
                    "saved successfully"
                )
            }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()