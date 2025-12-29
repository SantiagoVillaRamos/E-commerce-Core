"""
Adaptadores de Gateway para comunicación con otros módulos.
Este es el COMPONENTE CLAVE que conecta el módulo de Pedidos con el módulo de Catálogo.
"""
from loguru import logger
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.pedidos.domain.entities import OrderItem
from src.modules.pedidos.domain.gateways import InventoryGateway, StockReservationError

# Importaciones del módulo de Catálogo
from src.modules.catalogo.application.features.reserve_stock.command import (
    ReserveStockCommand, ReserveStockItemCommand
)
from src.modules.catalogo.application.features.reserve_stock.use_case import ReserveStockUseCase
from src.modules.catalogo.application.features.release_stock.command import (
    ReleaseStockCommand, ReleaseStockItemCommand
)
from src.modules.catalogo.application.features.release_stock.use_case import ReleaseStockUseCase
from src.modules.catalogo.infrastructure.repositories import SQLAlchemyProductRepository
from src.core.exceptions import BusinessRuleViolation, NotFoundError



class CatalogoInventoryGateway(InventoryGateway):
    """
    Adaptador del Gateway de Inventario que se comunica con el módulo de Catálogo.
    
    PATRÓN CLAVE: Este adaptador implementa el puerto InventoryGateway definido
    en el dominio de Pedidos, pero llama directamente a los Use Cases del módulo
    de Catálogo.
    
    Esto mantiene la separación de contextos delimitados mientras permite
    la comunicación interna del monolito.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Constructor con inyección de la sesión de base de datos.
        
        Args:
            db_session: Sesión de base de datos compartida
        """
        self.db_session = db_session
        
        # Crear el repositorio de productos
        self.product_repository = SQLAlchemyProductRepository(db_session)
        
        # Crear los use cases de stock
        self.reserve_stock_use_case = ReserveStockUseCase(self.product_repository)
        self.release_stock_use_case = ReleaseStockUseCase(self.product_repository)

    
    async def verify_and_reserve_stock(self, items: List[OrderItem]) -> bool:
        """
        Verifica disponibilidad y reserva stock llamando al módulo de Catálogo.
        
        Este método es el PUENTE entre los dos módulos.
        """
        try:
            # Convertir OrderItems a ReserveStockCommand
            reserve_items = [
                ReserveStockItemCommand(
                    product_id=item.product_id,
                    quantity=item.quantity.value
                )
                for item in items
            ]
            
            command = ReserveStockCommand(items=reserve_items)
            
            # LLAMADA AL MÓDULO DE CATÁLOGO
            response = await self.reserve_stock_use_case.execute(command)
            
            # Actualizar los OrderItems con la información obtenida del catálogo
            for i, product_info in enumerate(response.products):
                items[i].product_name = product_info.product_name
                items[i].unit_price = product_info.unit_price
            
            return response.success
            
        except NotFoundError as e:
            raise StockReservationError(f"Producto no encontrado: {e.message}")
        except BusinessRuleViolation as e:
            raise StockReservationError(f"No se pudo reservar stock: {e.message}")
        except Exception as e:
            raise StockReservationError(f"Error inesperado al reservar stock: {str(e)}")
    
    async def release_stock(self, items: List[OrderItem]) -> bool:
        """
        Libera stock previamente reservado.
        
        Este método llama al ReleaseStockUseCase del módulo de Catálogo
        para devolver el stock cuando se cancela una orden.
        """
        try:
            # Convertir OrderItems a ReleaseStockCommand
            release_items = [
                ReleaseStockItemCommand(
                    product_id=item.product_id,
                    quantity=item.quantity.value
                )
                for item in items
            ]
            
            command = ReleaseStockCommand(items=release_items)
            
            # LLAMADA AL MÓDULO DE CATÁLOGO
            response = await self.release_stock_use_case.execute(command)
            
            return response.success
            
        except NotFoundError as e:
            raise StockReservationError(f"Producto no encontrado: {e.message}")
        except Exception as e:
            raise StockReservationError(f"Error inesperado al liberar stock: {str(e)}")

    
    async def verify_product_exists(self, product_id: UUID) -> bool:
        """
        Verifica si un producto existe en el catálogo.
        """
        try:
            product = await self.product_repository.get_by_id(product_id)
            return product is not None
        except Exception:
            return False
