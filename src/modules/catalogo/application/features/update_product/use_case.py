"""
Caso de Uso: Actualizar Producto.
"""
from loguru import logger
from src.modules.catalogo.application.interfaces import IUpdateProductUseCase
from src.modules.catalogo.application.features.update_product.command import UpdateProductCommand
from src.modules.catalogo.application.features.update_product.response import UpdateProductResponse
from src.modules.catalogo.domain.repositories import ProductRepository
from src.modules.catalogo.domain.value_objects import SKU, Price, Stock
from src.core.exceptions import NotFoundError, BusinessRuleViolation

class UpdateProductUseCase(IUpdateProductUseCase):
    """
    Caso de Uso: Actualizar un producto existente.
    """
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        
    async def execute(self, command: UpdateProductCommand) -> UpdateProductResponse:
        """
        Actualiza los campos permitidos de un producto.
        """
        logger.info(f"Actualizando producto {command.product_id}")
        
        # 1. Obtener el producto existente
        product = await self.product_repository.get_by_id(command.product_id)
        if not product:
            raise NotFoundError("Product", str(command.product_id))
            
        # Actualizar campos de la entidad
        if command.name is not None:
            product.name = command.name
            
        if command.description is not None:
            product.description = command.description
            
        if command.price is not None or command.currency is not None:
            new_amount = command.price if command.price is not None else product.price.amount
            new_currency = command.currency if command.currency is not None else product.price.currency
            product.price = Price(amount=new_amount, currency=new_currency)
            
        if command.stock is not None:
            product.stock = Stock(quantity=command.stock)
            
        if command.is_active is not None:
            product.is_active = command.is_active
            
        # 6. Persistir cambios
        updated_product = await self.product_repository.update(product)
        logger.info(f"Producto {updated_product.product_id} actualizado exitosamente")
        
        return UpdateProductResponse(
            product_id=updated_product.product_id,
            sku=str(updated_product.sku),
            name=updated_product.name,
            description=updated_product.description,
            price=updated_product.price.amount,
            currency=updated_product.price.currency,
            stock=updated_product.stock.quantity,
            is_active=updated_product.is_active,
            updated_at=updated_product.updated_at
        )
