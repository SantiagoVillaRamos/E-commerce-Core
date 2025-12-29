from pydantic import BaseModel
from uuid import UUID

class UpdateOrderStatusResponse(BaseModel):
    """Respuesta a la actualización del estado."""
    order_id: UUID
    old_status: str
    new_status: str
    success: bool
    message: str
