from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class GetProductCommand(BaseModel):
    """Comando para obtener un producto por ID o SKU."""
    product_id: Optional[UUID] = None
    sku: Optional[str] = None
