"""
Command para cancelar una orden.
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class CancelOrderCommand:
    """
    Comando para cancelar una orden existente.
    
    Al cancelar una orden, se debe liberar el stock que había sido reservado.
    """
    order_id: UUID
    reason: Optional[str] = None
    
    def __post_init__(self):
        if not self.order_id:
            raise ValueError("El ID de la orden es obligatorio")
