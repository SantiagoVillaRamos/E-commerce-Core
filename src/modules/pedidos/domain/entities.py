"""
Entidades del dominio de Pedidos.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from src.modules.pedidos.domain.value_objects import (
    OrderStatus, Quantity, Address, CustomerInfo
)
from src.core.exceptions import BusinessRuleViolation


@dataclass
class OrderItem:
    """
    Item de una orden.
    Representa un producto específico dentro de un pedido.
    """
    product_id: UUID
    product_name: str
    quantity: Quantity
    unit_price: float  # Precio unitario al momento de la orden
    
    def __post_init__(self):
        if self.unit_price < 0:
            raise BusinessRuleViolation("El precio unitario no puede sea negativo")

    
    def calculate_subtotal(self) -> float:
        """Calcula el subtotal del item (cantidad * precio unitario)."""
        return round(self.quantity.value * self.unit_price, 2)
    
    def __repr__(self) -> str:
        return f"OrderItem(product={self.product_name}, qty={self.quantity.value}, price={self.unit_price})"


@dataclass
class Order:
    """
    Agregado Raíz: Orden de compra.
    Representa un pedido completo de un cliente.
    """
    # Identidad
    order_id: UUID = field(default_factory=uuid4)
    
    # Información del cliente
    customer_info: CustomerInfo = field(default=None)
    
    # Items de la orden
    items: List[OrderItem] = field(default_factory=list)
    
    # Dirección de envío
    shipping_address: Address = field(default=None)
    
    # Estado y totales
    status: OrderStatus = field(default=OrderStatus.PENDING)
    total_amount: float = field(default=0.0)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    confirmed_at: datetime = field(default=None)
    cancelled_at: datetime = field(default=None)
    
    def __post_init__(self):
        """Validaciones de la entidad."""
        if not self.items:
            raise BusinessRuleViolation("Una orden debe tener al menos un item")
        
        if self.customer_info is None:
            raise BusinessRuleViolation("La información del cliente es obligatoria")
        
        if self.shipping_address is None:
            raise BusinessRuleViolation("La dirección de envío es obligatoria")
        
        # Calcular total automáticamente
        if self.total_amount == 0.0:
            self.total_amount = self.calculate_total()
    
    # Métodos de negocio
    
    def calculate_total(self) -> float:
        """
        Calcula el total de la orden sumando todos los items.
        """
        total = sum(item.calculate_subtotal() for item in self.items)
        return round(total, 2)
    
    def confirm(self) -> None:
        """
        Confirma la orden.
        Regla de negocio: Solo se puede confirmar una orden en estado PENDING.
        """
        if self.status != OrderStatus.PENDING:
            raise BusinessRuleViolation(
                f"Solo se pueden confirmar órdenes en estado PENDING. Estado actual: {self.status}"
            )
        
        self.status = OrderStatus.CONFIRMED
        self.confirmed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason: str = None) -> None:
        """
        Cancela la orden.
        Regla de negocio: No se puede cancelar una orden ya enviada o entregada.
        """
        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise BusinessRuleViolation(
                f"No se puede cancelar una orden en estado {self.status}"
            )
        
        if self.status == OrderStatus.CANCELLED:
            raise BusinessRuleViolation("La orden ya está cancelada")
        
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_processing(self) -> None:
        """Marca la orden como en proceso."""
        if self.status != OrderStatus.CONFIRMED:
            raise BusinessRuleViolation("Solo se pueden procesar órdenes confirmadas")
        
        self.status = OrderStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def mark_as_shipped(self) -> None:
        """Marca la orden como enviada."""
        if self.status != OrderStatus.PROCESSING:
            raise BusinessRuleViolation("Solo se pueden enviar órdenes en proceso")
        
        self.status = OrderStatus.SHIPPED
        self.updated_at = datetime.utcnow()
    
    def mark_as_delivered(self) -> None:
        """Marca la orden como entregada."""
        if self.status != OrderStatus.SHIPPED:
            raise BusinessRuleViolation("Solo se pueden entregar órdenes enviadas")
        
        self.status = OrderStatus.DELIVERED
        self.updated_at = datetime.utcnow()
    
    def add_item(self, item: OrderItem) -> None:
        """Agrega un item a la orden (solo si está en PENDING)."""
        if self.status != OrderStatus.PENDING:
            raise BusinessRuleViolation("Solo se pueden agregar items a órdenes pendientes")
        
        self.items.append(item)
        self.total_amount = self.calculate_total()
        self.updated_at = datetime.utcnow()
    
    def get_item_count(self) -> int:
        """Retorna el número total de items (considerando cantidades)."""
        return sum(item.quantity.value for item in self.items)
