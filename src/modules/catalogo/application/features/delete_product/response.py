from pydantic import BaseModel
from uuid import UUID

class DeleteProductResponse(BaseModel):
    """Respuesta a la eliminación del producto."""
    product_id: UUID
    success: bool
    message: str
