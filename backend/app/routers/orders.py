from fastapi import APIRouter, HTTPException
from app.database.connection import get_connection
from app.models.order import (
    ProductionOrderCreate,
    ProductionOrderResponse
)

router = APIRouter(
    prefix="/api/orders",
    tags=["Production Orders"]
)


@router.post("/", response_model=ProductionOrderResponse)
def create_order(order: ProductionOrderCreate):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Check factory
            cur.execute(
                "SELECT factory_id FROM factories WHERE factory_id = %s",
                (order.factory_id,)
            )

            if cur.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Factory not found"
                )

            # Check product
            cur.execute(
                "SELECT product_id FROM products WHERE product_id = %s",
                (order.product_id,)
            )

            if cur.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            # Insert order
            cur.execute("""
                INSERT INTO production_orders
                (
                    order_id,
                    factory_id,
                    product_id,
                    quantity,
                    deadline,
                    minimum_quality,
                    carbon_budget_kg,
                    priority
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING status;
            """, (
                order.order_id,
                order.factory_id,
                order.product_id,
                order.quantity,
                order.deadline,
                order.minimum_quality,
                order.carbon_budget_kg,
                order.priority
            ))

            status = cur.fetchone()[0]

            conn.commit()

            return {
                **order.model_dump(),
                "status": status
            }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        conn.close()


@router.get("/")
def get_orders():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    order_id,
                    factory_id,
                    product_id,
                    quantity,
                    deadline,
                    minimum_quality,
                    carbon_budget_kg,
                    priority,
                    status,
                    created_at
                FROM production_orders
                ORDER BY created_at DESC;
            """)

            columns = [desc.name for desc in cur.description]

            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        conn.close()