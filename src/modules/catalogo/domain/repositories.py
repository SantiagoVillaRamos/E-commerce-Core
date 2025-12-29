"""
Puertos de Repositorio (Interfaces/Contratos).
Define CÓMO el dominio quiere persistir datos, sin saber DÓNDE ni CÓMO se implementa.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.modules.catalogo.domain.entities import Product
from src.modules.catalogo.domain.value_objects import SKU


class ProductRepository(ABC):
    """
    Puerto del Repositorio de Productos.
    Esta es una interfaz que será implementada en la capa de Infraestructura.
    """
    
    @abstractmethod
    async def save(self, product: Product) -> Product:
        """
        Guarda un nuevo producto.
        Retorna el producto guardado con su ID asignado.
        """
        pass
    
    @abstractmethod
    async def update(self, product: Product) -> Product:
        """
        Actualiza un producto existente.
        Retorna el producto actualizado.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """
        Busca un producto por su ID.
        Retorna None si no existe.
        """
        pass
    
    @abstractmethod
    async def get_by_sku(self, sku: SKU) -> Optional[Product]:
        """
        Busca un producto por su SKU.
        Retorna None si no existe.
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Obtiene todos los productos con paginación.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """
        Búsqueda avanzada con filtros dinámicos y búsqueda de texto.
        """
        pass
