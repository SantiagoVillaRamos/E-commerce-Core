"""
Puertos de Repositorio para el dominio de Pedidos.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.modules.pedidos.domain.entities import Order


class OrderRepository(ABC):
    """
    Puerto del Repositorio de Órdenes.
    Define el contrato de persistencia para órdenes.
    """
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """
        Guarda una nueva orden.
        Retorna la orden guardada con su ID asignado.
        """
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """
        Actualiza una orden existente.
        Retorna la orden actualizada.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """
        Busca una orden por su ID.
        Retorna None si no existe.
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtiene todas las órdenes con paginación.
        """
        pass

    @abstractmethod
    async def get_by_customer(self, customer_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtiene las órdenes de un cliente específico.
        """
        pass
