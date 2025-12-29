from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.catalogo.domain.entities import Product
from src.modules.catalogo.domain.value_objects import SKU
from src.modules.catalogo.domain.repositories import ProductRepository
from src.modules.catalogo.infrastructure.models import ProductModel
from src.modules.catalogo.infrastructure.mappers import ProductMapper
from src.core.exceptions import ConcurrencyError


class SQLAlchemyProductRepository(ProductRepository):
    """
    Implementación del ProductRepository usando SQLAlchemy.
    
    Responsabilidades:
    - Ejecutar operaciones CRUD en la base de datos
    - Delegar el mapeo a ProductMapper
    """
    
    def __init__(self, session: AsyncSession):
        """
        Constructor con inyección de la sesión de base de datos.
        
        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session
    
    # Implementación de los métodos del puerto
    
    async def save(self, product: Product) -> Product:
        """Guarda un nuevo producto en la base de datos."""
        model = ProductMapper.to_model(product)
        self.session.add(model)
        await self.session.flush()  # Para obtener el ID generado
        await self.session.refresh(model)
        return ProductMapper.to_domain(model)
    
    async def update(self, product: Product) -> Product:
        """
        Actualiza un producto existente con control de concurrencia optimista.
        """
        # Buscar el modelo existente
        stmt = select(ProductModel).where(ProductModel.product_id == product.product_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Producto con ID {product.product_id} no encontrado")
        
        # Incrementar versión para concurrencia optimista
        model.version = model.version + 1
        
        # Actualizar campos usando el mapper
        ProductMapper.update_model(model, product)
        
        await self.session.flush()
        await self.session.refresh(model)
        return ProductMapper.to_domain(model)

    
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Busca un producto por su ID (solo si no está borrado)."""
        stmt = select(ProductModel).where(
            ProductModel.product_id == product_id,
            ProductModel.deleted_at == None
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return ProductMapper.to_domain(model) if model else None
    
    async def get_by_sku(self, sku: SKU) -> Optional[Product]:
        """Busca un producto por su SKU (solo si no está borrado)."""
        stmt = select(ProductModel).where(
            ProductModel.sku == str(sku),
            ProductModel.deleted_at == None
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return ProductMapper.to_domain(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtiene todos los productos no borrados con paginación."""
        stmt = select(ProductModel).where(
            ProductModel.deleted_at == None
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [ProductMapper.to_domain(model) for model in models]
    
    async def delete(self, product_id: UUID) -> bool:
        """Realiza un BORRADO LÓGICO de un producto."""
        stmt = select(ProductModel).where(
            ProductModel.product_id == product_id,
            ProductModel.deleted_at == None
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        model.soft_delete()
        await self.session.flush()
        return True
    
    async def exists_by_sku(self, sku: SKU) -> bool:
        """Verifica si existe un producto con el SKU dado (no borrado)."""
        stmt = select(ProductModel.product_id).where(
            ProductModel.sku == str(sku),
            ProductModel.deleted_at == None
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def search(
        self,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """Búsqueda avanzada con filtros dinámicos."""
        stmt = select(ProductModel).where(ProductModel.deleted_at == None)
        
        if query:
            # Simulación de búsqueda de texto simple (mejorar con to_tsvector en Postgres real)
            stmt = stmt.where(
                (ProductModel.name.ilike(f"%{query}%")) | 
                (ProductModel.description.ilike(f"%{query}%"))
            )
        
        if min_price is not None:
            stmt = stmt.where(ProductModel.price_amount >= min_price)
            
        if max_price is not None:
            stmt = stmt.where(ProductModel.price_amount <= max_price)
            
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [ProductMapper.to_domain(model) for model in models]
