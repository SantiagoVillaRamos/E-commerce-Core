from pydantic import BaseModel
from uuid import UUID

class DeleteProductCommand(BaseModel):
    """Comando para eliminar o desactivar un producto."""
    product_id: UUID
    logical: bool = True  # Por defecto desactivación lógica (is_active=False)
