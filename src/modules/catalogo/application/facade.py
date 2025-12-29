"""
Facade del módulo Catálogo.
Proporciona un punto único de entrada para todas las operaciones del catálogo.
"""
from typing import List

from src.modules.catalogo.application.interfaces import (
    ICreateProductUseCase,
    IListProductsUseCase,
    IReserveStockUseCase
)
from src.modules.catalogo.domain.entities import Product
from src.modules.catalogo.application.features.create_product.command import CreateProductCommand
from src.modules.catalogo.application.features.reserve_stock.command import ReserveStockCommand
from src.modules.catalogo.application.features.reserve_stock.response import ReserveStockResponse


class CatalogoFacade:
    """
    Facade para el módulo de Catálogo.
    
    Responsabilidades:
    1. Proporcionar una API simplificada para operaciones del catálogo
    2. Orquestar llamadas a múltiples casos de uso si es necesario
    3. Servir como punto único de entrada al módulo
    """
    
    def __init__(
        self,
        create_product_use_case: ICreateProductUseCase,
        list_products_use_case: IListProductsUseCase,
        reserve_stock_use_case: IReserveStockUseCase
    ):
        """
        Constructor con inyección de dependencias.
        
        Args:
            create_product_use_case: Caso de uso para crear productos
            list_products_use_case: Caso de uso para listar productos
            reserve_stock_use_case: Caso de uso para reservar stock
        """
        self._create_product = create_product_use_case
        self._list_products = list_products_use_case
        self._reserve_stock = reserve_stock_use_case
    
    # ==================== Operaciones de Productos ====================
    
    async def create_product(self, command: CreateProductCommand) -> Product:
        """
        Crea un nuevo producto en el catálogo.
        
        Args:
            command: Datos del producto a crear
            
        Returns:
            Entidad de dominio Product creada
            
        Raises:
            BusinessRuleViolation: Si el SKU ya existe o hay violaciones de negocio
            ValidationError: Si los datos no son válidos
        """
        return await self._create_product.execute(command)
    
    async def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Lista productos del catálogo.
        
        Args:
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de entidades de dominio Product
        """
        return await self._list_products.execute(skip, limit)
    
    # ==================== Operaciones de Stock ====================
    
    async def reserve_stock(self, command: ReserveStockCommand) -> ReserveStockResponse:
        """
        Reserva stock de productos.
        
        Esta operación es crítica para la comunicación entre módulos.
        Es llamada por el módulo de Pedidos.
        
        Args:
            command: Datos de los productos y cantidades a reservar
            
        Returns:
            Respuesta con el resultado de la reserva
            
        Raises:
            NotFoundError: Si algún producto no existe
            BusinessRuleViolation: Si no hay stock suficiente
        """
        return await self._reserve_stock.execute(command)

