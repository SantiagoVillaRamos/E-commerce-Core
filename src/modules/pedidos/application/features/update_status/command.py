from pydantic import BaseModel
from uuid import UUID

class UpdateOrderStatusCommand(BaseModel):
    """Comando para actualizar el estado de una orden."""
    order_id: UUID
    new_status: str
