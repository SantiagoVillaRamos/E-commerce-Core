"""
Interfaces (Puertos) para los Casos de Uso del módulo Catálogo.
Estas interfaces permiten la inversión de dependencias (Dependency Inversion Principle).
"""
from abc import ABC, abstractmethod
from typing import List

from src.modules.catalogo.application.features.create_product.command import CreateProductCommand
from src.modules.catalogo.domain.entities import Product
from src.modules.catalogo.application.features.reserve_stock.command import ReserveStockCommand
from src.modules.catalogo.application.features.reserve_stock.response import ReserveStockResponse
from src.modules.catalogo.application.features.release_stock.command import ReleaseStockCommand
from src.modules.catalogo.application.features.release_stock.response import ReleaseStockResponse
from src.modules.catalogo.application.features.get_product.command import GetProductCommand
from src.modules.catalogo.application.features.get_product.response import GetProductResponse
from src.modules.catalogo.application.features.update_product.command import UpdateProductCommand
from src.modules.catalogo.application.features.update_product.response import UpdateProductResponse
from src.modules.catalogo.application.features.delete_product.command import DeleteProductCommand
from src.modules.catalogo.application.features.delete_product.response import DeleteProductResponse



class ICreateProductUseCase(ABC):
    """
    Interfaz para el caso de uso de crear producto.
    
    Esta interfaz define el contrato que debe cumplir cualquier
    implementación del caso de uso de creación de productos.
    """
    
    @abstractmethod
    async def execute(self, command: CreateProductCommand) -> Product:
        """
        Ejecuta la creación de un producto.
        
        Args:
            command: Datos del producto a crear
            
        Returns:
            Entidad de dominio Product creada
            
        Raises:
            BusinessRuleViolation: Si el SKU ya existe o hay violaciones de negocio
            ValidationError: Si los datos no son válidos
        """
        pass


class IListProductsUseCase(ABC):
    """
    Interfaz para el caso de uso de listar productos.
    
    Esta interfaz define el contrato que debe cumplir cualquier
    implementación del caso de uso de listado de productos.
    """
    
    @abstractmethod
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Ejecuta el listado de productos.
        
        Args:
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de entidades de dominio Product
        """
        pass


class IReserveStockUseCase(ABC):
    """
    Interfaz para el caso de uso de reservar stock.
    
    Esta interfaz define el contrato que debe cumplir cualquier
    implementación del caso de uso de reserva de stock.
    """
    
    @abstractmethod
    async def execute(self, command: ReserveStockCommand) -> ReserveStockResponse:
        """
        Ejecuta la reserva de stock.
        
        Args:
            command: Datos de los productos y cantidades a reservar
            
        Returns:
            Respuesta con el resultado de la reserva
            
        Raises:
            NotFoundError: Si algún producto no existe
            BusinessRuleViolation: Si no hay stock suficiente
        """
        pass


class IReleaseStockUseCase(ABC):
    """
    Interfaz para el caso de uso de liberar stock.
    
    Esta interfaz define el contrato que debe cumplir cualquier
    implementación del caso de uso de liberación de stock.
    """
    
    @abstractmethod
    async def execute(self, command: ReleaseStockCommand) -> ReleaseStockResponse:
        """
        Ejecuta la liberación de stock.
        
        Args:
            command: Datos de los productos y cantidades a liberar
            
        Returns:
            Respuesta con el resultado de la liberación
            
        Raises:
            NotFoundError: Si algún producto no existe
        """
        pass


class IGetProductUseCase(ABC):
    """Interfaz para el caso de uso de obtener producto."""
    @abstractmethod
    async def execute(self, command: GetProductCommand) -> GetProductResponse:
        pass


class IUpdateProductUseCase(ABC):
    """Interfaz para el caso de uso de actualizar producto."""
    @abstractmethod
    async def execute(self, command: UpdateProductCommand) -> UpdateProductResponse:
        pass


class IDeleteProductUseCase(ABC):
    """Interfaz para el caso de uso de eliminar producto."""
    @abstractmethod
    async def execute(self, command: DeleteProductCommand) -> DeleteProductResponse:
        pass

