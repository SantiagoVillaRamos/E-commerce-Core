"""
Command para liberar stock de productos.
"""
from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass
class ReleaseStockItemCommand:
    """
    Representa un item cuyo stock debe ser liberado.
    """
    product_id: UUID
    quantity: int
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")


@dataclass
class ReleaseStockCommand:
    """
    Comando para liberar stock de múltiples productos.
    
    Este comando se usa cuando se cancela una orden y necesitamos
    devolver el stock que había sido reservado.
    """
    items: List[ReleaseStockItemCommand]
    
    def __post_init__(self):
        if not self.items:
            raise ValueError("Debe haber al menos un item para liberar stock")
