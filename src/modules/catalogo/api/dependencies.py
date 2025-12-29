"""
Funciones de Inyección de Dependencias para el módulo de Catálogo.
Usa Singleton para repositorios y Facade como punto de entrada.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from src.core.database import get_db_session
from src.modules.catalogo.infrastructure.repository_manager import RepositoryManager
from src.modules.catalogo.application.facade import CatalogoFacade

# Casos de Uso
from src.modules.catalogo.application.features.create_product.use_case import CreateProductUseCase
from src.modules.catalogo.application.features.list_products.use_case import ListProductsUseCase
from src.modules.catalogo.application.features.reserve_stock.use_case import ReserveStockUseCase
from src.modules.catalogo.application.features.get_product.use_case import GetProductUseCase
from src.modules.catalogo.application.features.update_product.use_case import UpdateProductUseCase
from src.modules.catalogo.application.features.delete_product.use_case import DeleteProductUseCase


# ==================== Singleton Repository Manager ====================

def get_repository_manager() -> RepositoryManager:
    """
    Obtiene la instancia Singleton del gestor de repositorios.
    
    Returns:
        Instancia única del RepositoryManager
    """
    return RepositoryManager()


# ==================== Facade ====================

async def get_catalogo_facade(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    repo_manager: Annotated[RepositoryManager, Depends(get_repository_manager)]
) -> CatalogoFacade:
    """
    Inyecta la Facade del módulo Catálogo.
    
    Esta función:
    1. Obtiene el repositorio desde el Singleton
    2. Crea instancias de los casos de uso
    3. Construye y retorna la Facade
    
    Args:
        session: Sesión de base de datos (inyectada por FastAPI)
        repo_manager: Gestor Singleton de repositorios
        
    Returns:
        Instancia configurada de CatalogoFacade
    """
    # Obtener repositorio desde el Singleton
    product_repository = repo_manager.get_product_repository(session)
    
    # Crear casos de uso con el repositorio
    create_product_uc = CreateProductUseCase(product_repository)
    list_products_uc = ListProductsUseCase(product_repository)
    reserve_stock_uc = ReserveStockUseCase(product_repository)
    get_product_uc = GetProductUseCase(product_repository)
    update_product_uc = UpdateProductUseCase(product_repository)
    delete_product_uc = DeleteProductUseCase(product_repository)
    
    # Construir y retornar la Facade
    return CatalogoFacade(
        create_product_use_case=create_product_uc,
        list_products_use_case=list_products_uc,
        reserve_stock_use_case=reserve_stock_uc,
        get_product_use_case=get_product_uc,
        update_product_use_case=update_product_uc,
        delete_product_use_case=delete_product_uc
    )

