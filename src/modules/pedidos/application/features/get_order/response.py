from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class OrderItemResponse(BaseModel):
    """DTO de salida para un item de orden."""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

class GetOrderResponse(BaseModel):
    """
    Respuesta con los detalles completos de una orden.
    """
    order_id: UUID
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    items: List[OrderItemResponse]
    total_amount: float
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
