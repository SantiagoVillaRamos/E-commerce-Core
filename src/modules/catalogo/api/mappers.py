"""
Mappers de la capa API para el módulo de Catálogo.
Responsable de convertir entre DTOs (Commands/Responses) y entidades de dominio.

IMPORTANTE: Estos mappers pertenecen a la capa de API, NO a la capa de aplicación.
Los casos de uso trabajan directamente con entidades de dominio.
"""
from src.modules.catalogo.application.features.create_product.command import CreateProductCommand
from src.modules.catalogo.application.features.create_product.response import CreateProductResponse
from src.modules.catalogo.application.features.get_product.response import GetProductResponse
from src.modules.catalogo.application.features.update_product.response import UpdateProductResponse
from src.modules.catalogo.application.features.delete_product.response import DeleteProductResponse
from src.modules.catalogo.domain.entities import Product


class ProductDTOMapper:
    """
    Mapper estático para convertir entre DTOs y entidades de dominio.
    """
    
    @staticmethod
    def domain_to_response(product: Product) -> CreateProductResponse:
        """Convierte una entidad Product a CreateProductResponse."""
        return CreateProductResponse(
            product_id=product.product_id,
            sku=str(product.sku),
            name=product.name,
            description=product.description,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock.quantity,
            is_active=product.is_active,
            created_at=product.created_at
        )

    @staticmethod
    def domain_to_get_response(product: Product) -> GetProductResponse:
        """Convierte una entidad Product a GetProductResponse."""
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

    @staticmethod
    def domain_to_update_response(product: Product) -> UpdateProductResponse:
        """Convierte una entidad Product a UpdateProductResponse."""
        return UpdateProductResponse(
            product_id=product.product_id,
            sku=str(product.sku),
            name=product.name,
            description=product.description,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock.quantity,
            is_active=product.is_active,
            updated_at=product.updated_at
        )
