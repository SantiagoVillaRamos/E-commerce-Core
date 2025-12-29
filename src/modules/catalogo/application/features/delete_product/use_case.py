"""
Caso de Uso: Eliminar/Desactivar Producto.
"""
from loguru import logger
from src.modules.catalogo.application.interfaces import IDeleteProductUseCase
from src.modules.catalogo.application.features.delete_product.command import DeleteProductCommand
from src.modules.catalogo.application.features.delete_product.response import DeleteProductResponse
from src.modules.catalogo.domain.repositories import ProductRepository
from src.core.exceptions import NotFoundError

class DeleteProductUseCase(IDeleteProductUseCase):
    """
    Caso de Uso: Eliminar o desactivar un producto.
    """
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        
    async def execute(self, command: DeleteProductCommand) -> DeleteProductResponse:
        """
        Ejecuta la eliminación o desactivación.
        """
        logger.info(f"Iniciando eliminación de producto {command.product_id} (lógica={command.logical})")
        
        # 1. Obtener el producto
        product = await self.product_repository.get_by_id(command.product_id)
        if not product:
            raise NotFoundError("Product", str(command.product_id))
            
        if command.logical:
            # Desactivación lógica
            product.deactivate()
            await self.product_repository.update(product)
            logger.info(f"Producto {command.product_id} desactivado lógicamente")
            return DeleteProductResponse(
                product_id=command.product_id,
                success=True,
                message="Producto desactivado exitosamente (lógico)"
            )
        else:
            # Eliminación física
            success = await self.product_repository.delete(command.product_id)
            logger.info(f"Producto {command.product_id} eliminado físicamente (éxito: {success})")
            return DeleteProductResponse(
                product_id=command.product_id,
                success=success,
                message="Producto eliminado físicamente" if success else "No se pudo eliminar el producto"
            )
