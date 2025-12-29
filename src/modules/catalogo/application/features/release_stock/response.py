"""
Response para la operación de liberar stock.
"""
from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass
class ProductStockInfo:
    """
    Información sobre el stock de un producto después de liberarlo.
    """
    product_id: UUID
    product_name: str
    sku: str
    released_quantity: int
    current_stock: int  # Stock actual después de liberar


@dataclass
class ReleaseStockResponse:
    """
    Respuesta de la operación de liberar stock.
    """
    success: bool
    products: List[ProductStockInfo]
    message: str
