"""
Modelos de SQLAlchemy para el módulo de Catálogo.
Estos modelos representan la estructura de la base de datos.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Uuid
from datetime import datetime
import uuid

from src.core.database import Base, SoftDeleteMixin


class ProductModel(Base, SoftDeleteMixin):
    """
    Modelo de base de datos para Product.
    Mapea la entidad de dominio a la tabla de PostgreSQL.
    """
    __tablename__ = "products"
    
    # Identidad
    product_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False, default="")
    
    # Precio (desnormalizado por simplicidad)
    price_amount = Column(Float, nullable=False)
    price_currency = Column(String(3), nullable=False, default="USD")
    
    # Stock
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # Estado
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Control de concurrencia optimista
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    def __repr__(self):
        return f"<ProductModel(sku='{self.sku}', name='{self.name}')>"
