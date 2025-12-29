from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class GetProductResponse(BaseModel):
    """Respuesta con los datos del producto."""
    product_id: UUID
    sku: str
    name: str
    description: str
    price: float
    currency: str
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
