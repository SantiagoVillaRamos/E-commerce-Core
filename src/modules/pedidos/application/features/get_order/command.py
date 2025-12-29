from pydantic import BaseModel
from uuid import UUID

class GetOrderCommand(BaseModel):
    """Comando para obtener una orden por ID."""
    order_id: UUID
