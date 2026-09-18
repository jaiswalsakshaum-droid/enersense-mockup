from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProductionOrderCreate(BaseModel):
    order_id: str
    factory_id: str
    product_id: str
    quantity: int
    deadline: datetime
    minimum_quality: Optional[float] = 95
    carbon_budget_kg: Optional[float] = None
    priority: str = "NORMAL"


class ProductionOrderResponse(ProductionOrderCreate):
    status: str