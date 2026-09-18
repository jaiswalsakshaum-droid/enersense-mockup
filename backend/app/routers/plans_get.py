from fastapi import APIRouter, HTTPException

from app.database.connection import get_connection


router = APIRouter(
    prefix="/api/plans",
    tags=["Production Plans"]
)


@router.get("/{plan_id}")
def get_plan(plan_id: str):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Get plan
            cur.execute("""
                SELECT
                    plan_id,
                    order_id,
                    status,
                    total_cost_inr,
                    total_energy_kwh,
                    total_carbon_kg,
                    completion_time,
                    quality_percent,
                    peak_demand_kw,
                    created_at
                FROM production_plans
                WHERE plan_id = %s;
            """, (plan_id,))

            plan = cur.fetchone()

            if not plan:
                raise HTTPException(
                    status_code=404,
                    detail="Production plan not found"
                )

            columns = [desc.name for desc in cur.description]

            plan_data = dict(zip(columns, plan))

            # Get operations
            cur.execute("""
                SELECT
                    operation_id,
                    machine_id,
                    product_id,
                    quantity,
                    start_time,
                    end_time,
                    energy_kwh,
                    cost_inr,
                    carbon_kg,
                    expected_defects
                FROM plan_operations
                WHERE plan_id = %s
                ORDER BY start_time;
            """, (plan_id,))

            operations = cur.fetchall()

            operation_columns = [
                desc.name for desc in cur.description
            ]

            plan_data["operations"] = [
                dict(zip(operation_columns, row))
                for row in operations
            ]

            return plan_data

    finally:
        conn.close()