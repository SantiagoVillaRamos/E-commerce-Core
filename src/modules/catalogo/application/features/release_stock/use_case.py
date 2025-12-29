"""
Caso de Uso: Liberar Stock de Productos.
Este use case es llamado cuando se cancela una orden y necesitamos
devolver el stock que había sido reservado.
"""
from typing import List

from src.modules.catalogo.application.interfaces import IReleaseStockUseCase
from src.modules.catalogo.application.features.release_stock.command import ReleaseStockCommand
from src.modules.catalogo.application.features.release_stock.response import (
    ReleaseStockResponse, ProductStockInfo
)
from src.modules.catalogo.domain.repositories import ProductRepository
from src.core.exceptions import NotFoundError


class ReleaseStockUseCase(IReleaseStockUseCase):
    """
    Caso de Uso: Liberar stock de múltiples productos.
    
    Este use case es el complemento de ReserveStockUseCase.
    Se llama cuando se cancela una orden para devolver el stock reservado.
    
    Responsabilidades:
    1. Verificar que todos los productos existan
    2. Liberar el stock (incrementar la cantidad disponible)
    3. Actualizar los productos en la base de datos
    4. Operación transaccional: todo o nada
    """
    
    def __init__(self, product_repository: ProductRepository):
        """
        Constructor con Inyección de Dependencias.
        
        Args:
            product_repository: Implementación del puerto ProductRepository
        """
        self.product_repository = product_repository
    
    async def execute(self, command: ReleaseStockCommand) -> ReleaseStockResponse:
        """
        Ejecuta el caso de uso.
        
        Args:
            command: Datos de entrada con los items a liberar
            
        Returns:
            ReleaseStockResponse con el resultado de la liberación
            
        Raises:
            NotFoundError: Si algún producto no existe
        """
        products_info: List[ProductStockInfo] = []
        
        # Fase 1: Verificar que todos los productos existan
        for item in command.items:
            product = await self.product_repository.get_by_id(item.product_id)
            
            if not product:
                raise NotFoundError("Product", str(item.product_id))
        
        # Fase 2: Liberar stock (si llegamos aquí, todos los productos existen)
        for item in command.items:
            product = await self.product_repository.get_by_id(item.product_id)
            
            # Liberar stock (esto incrementa la cantidad)
            product.release_stock(item.quantity)
            
            # Actualizar en la base de datos
            updated_product = await self.product_repository.update(product)
            
            # Agregar información del producto
            products_info.append(
                ProductStockInfo(
                    product_id=updated_product.product_id,
                    product_name=updated_product.name,
                    sku=str(updated_product.sku),
                    released_quantity=item.quantity,
                    current_stock=updated_product.stock.quantity
                )
            )
        
        return ReleaseStockResponse(
            success=True,
            products=products_info,
            message=f"Stock liberado exitosamente para {len(products_info)} producto(s)"
        )
