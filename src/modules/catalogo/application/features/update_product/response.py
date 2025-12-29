from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class UpdateProductResponse(BaseModel):
    """Respuesta con los datos del producto actualizado."""
    product_id: UUID
    sku: str
    name: str
    description: str
    price: float
    currency: str
    stock: int
    is_active: bool
    updated_at: datetime
