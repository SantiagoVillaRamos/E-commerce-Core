"""
Router de FastAPI para el módulo de Catálogo.
Define los endpoints HTTP para gestionar productos.
"""
from fastapi import APIRouter, Depends, status
from typing import List, Annotated

from src.modules.catalogo.application.facade import CatalogoFacade
from src.modules.catalogo.application.features.create_product.command import CreateProductCommand
from src.modules.catalogo.application.features.create_product.response import CreateProductResponse
from src.modules.catalogo.application.features.get_product.command import GetProductCommand
from src.modules.catalogo.application.features.get_product.response import GetProductResponse
from src.modules.catalogo.application.features.update_product.command import UpdateProductCommand
from src.modules.catalogo.application.features.update_product.response import UpdateProductResponse
from src.modules.catalogo.application.features.delete_product.command import DeleteProductCommand
from src.modules.catalogo.application.features.delete_product.response import DeleteProductResponse
from src.modules.catalogo.api.dependencies import get_catalogo_facade


from src.modules.catalogo.api.mappers import ProductDTOMapper

# Router del módulo
router = APIRouter()


@router.post(
    "/products",
    response_model=CreateProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    description="Crea un nuevo producto en el catálogo con validación de SKU único"
)
async def create_product(
    command: CreateProductCommand,
    facade: Annotated[CatalogoFacade, Depends(get_catalogo_facade)]
) -> CreateProductResponse:
    """
    Crea un nuevo producto en el catálogo.
    
    Las excepciones son manejadas automáticamente por los exception handlers globales.
    
    Args:
        command: Datos del producto a crear
        facade: Facade del módulo inyectada automáticamente
        
    Returns:
        Datos del producto creado
    """
    
    # 1. Pasar la entidad a la facade
    saved_product = await facade.create_product(command)
    
    # 2. Mapear a DTO de respuesta
    return ProductDTOMapper.domain_to_response(saved_product)


@router.get(
    "/products",
    response_model=List[CreateProductResponse],
    summary="Listar productos",
    description="Obtiene una lista paginada de productos"
)
async def list_products(
    facade: Annotated[CatalogoFacade, Depends(get_catalogo_facade)],
    skip: int = 0,
    limit: int = 100
) -> List[CreateProductResponse]:
    """
    Endpoint para listar productos.
    Usa la Facade del módulo Catálogo.
    
    Args:
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        facade: Facade del módulo inyectada automáticamente
        
    Returns:
        Lista de productos
    """
    # La facade retorna una lista de entidades de dominio
    products = await facade.list_products(skip, limit)
    
    # Mapeamos a lista de DTOs de respuesta
    return [ProductDTOMapper.domain_to_response(p) for p in products]


@router.get(
    "/products/{product_id}",
    response_model=GetProductResponse,
    summary="Obtener producto por ID",
    description="Busca un producto específico por su UUID"
)
async def get_product_by_id(
    product_id: str,
    facade: Annotated[CatalogoFacade, Depends(get_catalogo_facade)]
) -> GetProductResponse:
    """Obtiene un producto por su ID."""
    command = GetProductCommand(product_id=product_id)
    return await facade.get_product(command)


@router.get(
    "/products/sku/{sku}",
    response_model=GetProductResponse,
    summary="Obtener producto por SKU",
    description="Busca un producto específico por su SKU"
)
async def get_product_by_sku(
    sku: str,
    facade: Annotated[CatalogoFacade, Depends(get_catalogo_facade)]
) -> GetProductResponse:
    """Obtiene un producto por su SKU."""
    command = GetProductCommand(sku=sku)
    return await facade.get_product(command)


@router.put(
    "/products/{product_id}",
    response_model=UpdateProductResponse,
    summary="Actualizar producto",
    description="Actualiza campos de un producto existente"
)
async def update_product(
    product_id: str,
    command: UpdateProductCommand,
    facade: Annotated[CatalogoFacade, Depends(get_catalogo_facade)]
) -> UpdateProductResponse:
    """Actualiza un producto."""
    if str(command.product_id) != product_id:
        command.product_id = product_id
    return await facade.update_product(command)


@router.delete(
    "/products/{product_id}",
    response_model=DeleteProductResponse,
    summary="Eliminar producto",
    description="Elimina o desactiva un producto"
)
async def delete_product(
    product_id: str,
    facade: Annotated[CatalogoFacade, Depends(get_catalogo_facade)],
    logical: bool = True
) -> DeleteProductResponse:
    """Elimina un producto."""
    command = DeleteProductCommand(product_id=product_id, logical=logical)
    return await facade.delete_product(command)


@router.get(
    "/health",
    summary="Health check del módulo Catálogo"
)
async def health_check():
    """Endpoint de salud del módulo."""
    return {
        "module": "catalogo",
        "status": "healthy"
    }
