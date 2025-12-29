from pydantic import BaseModel
from typing import List
from src.modules.pedidos.application.features.get_order.response import GetOrderResponse

class GetOrdersByCustomerResponse(BaseModel):
    """Respuesta con la lista de órdenes del cliente."""
    customer_id: str
    orders: List[GetOrderResponse]
    total: int
