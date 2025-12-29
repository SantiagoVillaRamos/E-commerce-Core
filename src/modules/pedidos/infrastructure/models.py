"""
Modelos de SQLAlchemy para el módulo de Pedidos.
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum, Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.core.database import Base


class OrderStatusEnum(str, enum.Enum):
    """Enum para el estado de la orden (para SQLAlchemy)."""
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"



class OrderModel(Base):
    """
    Modelo de base de datos para Order.
    """
    __tablename__ = "orders"
    
    # Identidad
    order_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Información del cliente
    customer_id = Column(String(100), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    
    # Dirección de envío
    shipping_street = Column(String(500), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(100), nullable=False, default="Colombia")
    
    # Estado y totales
    status = Column(SQLEnum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.pending)
    total_amount = Column(Float, nullable=False)
    
    # Control de concurrencia optimista
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    
    # Relación con items
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<OrderModel(order_id='{self.order_id}', customer='{self.customer_name}', status='{self.status}')>"


class OrderItemModel(Base):
    """
    Modelo de base de datos para OrderItem.
    """
    __tablename__ = "order_items"
    
    # Identidad
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Uuid, ForeignKey("orders.order_id"), nullable=False)
    
    # Información del producto
    product_id = Column(Uuid, nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    # Relación con orden
    order = relationship("OrderModel", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItemModel(product='{self.product_name}', qty={self.quantity})>"
