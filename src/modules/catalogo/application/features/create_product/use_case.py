"""
Caso de Uso: Crear Producto.
Orquesta la lógica de aplicación para crear un producto.
"""
from src.modules.catalogo.application.features.create_product.command import CreateProductCommand
from src.modules.catalogo.application.interfaces import ICreateProductUseCase
from src.modules.catalogo.domain.entities import Product
from src.modules.catalogo.domain.factories import ProductFactory
from src.modules.catalogo.domain.repositories import ProductRepository
from src.core.exceptions import BusinessRuleViolation
from loguru import logger


class CreateProductUseCase(ICreateProductUseCase):
    """
    Caso de Uso: Crear un nuevo producto en el catálogo.
    
    Responsabilidades:
    1. Validar que el SKU no exista
    2. Crear la entidad Product con los Value Objects
    3. Persistir usando el repositorio
    """
        
    def __init__(self, product_repository: ProductRepository):
        """
        Constructor con Inyección de Dependencias.
        
        Args:
            product_repository: Implementación del puerto ProductRepository
        """
        self.product_repository = product_repository
    
    async def execute(self, command: CreateProductCommand) -> Product:
        """
        Ejecuta el caso de uso.
        
        Args:
            command: Datos del producto a crear
            
        Returns:
            Entidad de dominio Product creada
            
        Raises:
            BusinessRuleViolation: Si el SKU ya existe o hay violaciones de negocio
        """
        logger.info(f"Creando nuevo producto con SKU: {command.sku}")

        product = ProductFactory.create_from_primitives(
                sku=command.sku,
                name=command.name,
                description=command.description,
                price=command.price,
                currency=command.currency,
                initial_stock=command.initial_stock
            )
        
        # 1. Verificar que el SKU no exista (regla de negocio)
        if await self.product_repository.exists_by_sku(product.sku):
            raise BusinessRuleViolation(
                f"Ya existe un producto con el SKU: {product.sku}"
            )
        
        # 2. Persistir y retornar la entidad de dominio
        return await self.product_repository.save(product)
