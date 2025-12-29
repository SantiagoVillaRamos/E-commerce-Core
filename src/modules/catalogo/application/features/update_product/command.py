from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class UpdateProductCommand(BaseModel):
    """Comando para actualizar un producto."""
    product_id: UUID
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
