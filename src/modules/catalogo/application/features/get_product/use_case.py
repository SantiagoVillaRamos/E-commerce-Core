"""
Caso de Uso: Obtener Producto.
Permite buscar un producto por su ID único o por su SKU.
"""
from src.modules.catalogo.application.interfaces import IGetProductUseCase
from src.modules.catalogo.application.features.get_product.command import GetProductCommand
from src.modules.catalogo.application.features.get_product.response import GetProductResponse
from src.modules.catalogo.domain.repositories import ProductRepository
from src.core.exceptions import NotFoundError, ValidationError

class GetProductUseCase(IGetProductUseCase):
    """
    Caso de Uso: Obtener un producto del catálogo.
    """
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        
    async def execute(self, command: GetProductCommand) -> GetProductResponse:
        """
        Busca un producto según los criterios del comando.
        """
        if not command.product_id and not command.sku:
            raise ValidationError("Debe proporcionar product_id o sku")
            
        product = None
        
        if command.product_id:
            product = await self.product_repository.get_by_id(command.product_id)
            if not product:
                raise NotFoundError("Product", str(command.product_id))
        else:
            product = await self.product_repository.get_by_sku(command.sku)
            if not product:
                raise NotFoundError("Product", command.sku)
                
        return GetProductResponse(
            product_id=product.product_id,
            sku=str(product.sku),
            name=product.name,
            description=product.description,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock.quantity,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
