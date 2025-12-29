"""
Response para la operación de cancelar orden.
"""
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class CancelOrderResponse:
    """
    Respuesta de la operación de cancelar orden.
    """
    order_id: UUID
    status: str
    cancelled_at: datetime
    reason: str
    stock_released: bool
    message: str
