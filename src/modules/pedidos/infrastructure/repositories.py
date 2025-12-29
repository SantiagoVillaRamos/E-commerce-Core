"""
Adaptador del Repositorio de Órdenes usando SQLAlchemy.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.pedidos.domain.entities import Order, OrderItem
from src.modules.pedidos.domain.value_objects import (
    OrderStatus, Quantity, Address, CustomerInfo
)
from src.modules.pedidos.domain.repositories import OrderRepository
from src.modules.pedidos.infrastructure.models import OrderModel, OrderItemModel, OrderStatusEnum


class SQLAlchemyOrderRepository(OrderRepository):
    """
    Implementación del OrderRepository usando SQLAlchemy.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Constructor con inyección de la sesión de base de datos.
        
        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session
    
    # Métodos de mapeo (Domain <-> ORM)
    
    def _to_domain(self, model: OrderModel) -> Order:
        """Convierte un OrderModel (ORM) a Order (Dominio)."""
        # Mapear items
        items = [
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=Quantity(value=item.quantity),
                unit_price=item.unit_price
            )
            for item in model.items
        ]
        
        # Mapear orden
        return Order(
            order_id=model.order_id,
            customer_info=CustomerInfo(
                customer_id=model.customer_id,
                name=model.customer_name,
                email=model.customer_email,
                phone=model.customer_phone
            ),
            items=items,
            shipping_address=Address(
                street=model.shipping_street,
                city=model.shipping_city,
                state=model.shipping_state,
                postal_code=model.shipping_postal_code,
                country=model.shipping_country
            ),
            status=OrderStatus(model.status.value),
            total_amount=model.total_amount,
            created_at=model.created_at,
            updated_at=model.updated_at,
            confirmed_at=model.confirmed_at
        )
    
    def _to_model(self, order: Order) -> OrderModel:
        """Convierte un Order (Dominio) a OrderModel (ORM)."""
        # Crear modelo de orden
        order_model = OrderModel(
            order_id=order.order_id,
            customer_id=order.customer_info.customer_id,
            customer_name=order.customer_info.name,
            customer_email=order.customer_info.email,
            customer_phone=order.customer_info.phone,
            shipping_street=order.shipping_address.street,
            shipping_city=order.shipping_address.city,
            shipping_state=order.shipping_address.state,
            shipping_postal_code=order.shipping_address.postal_code,
            shipping_country=order.shipping_address.country,
            status=OrderStatusEnum(order.status.value),
            total_amount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            confirmed_at=order.confirmed_at
        )
        
        # Crear modelos de items
        for item in order.items:
            item_model = OrderItemModel(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity.value,
                unit_price=item.unit_price
            )
            order_model.items.append(item_model)
        
        return order_model
    
    # Implementación de los métodos del puerto
    
    async def save(self, order: Order) -> Order:
        """Guarda una nueva orden en la base de datos."""
        model = self._to_model(order)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model, ["items"])
        return self._to_domain(model)
    
    async def update(self, order: Order) -> Order:
        """Actualiza una orden existente."""
        stmt = select(OrderModel).where(OrderModel.order_id == order.order_id).options(selectinload(OrderModel.items))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Orden con ID {order.order_id} no encontrada")
        
        # Actualizar campos
        model.customer_id = order.customer_info.customer_id
        model.customer_name = order.customer_info.name
        model.customer_email = order.customer_info.email
        model.customer_phone = order.customer_info.phone
        model.shipping_street = order.shipping_address.street
        model.shipping_city = order.shipping_address.city
        model.shipping_state = order.shipping_address.state
        model.shipping_postal_code = order.shipping_address.postal_code
        model.shipping_country = order.shipping_address.country
        model.status = OrderStatusEnum(order.status.value)
        model.total_amount = order.total_amount
        model.updated_at = order.updated_at
        model.confirmed_at = order.confirmed_at
        
        # Incrementar versión para concurrencia optimista
        model.version = model.version + 1

        
        await self.session.flush()
        await self.session.refresh(model, ["items"])
        return self._to_domain(model)

    
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Busca una orden por su ID."""
        stmt = select(OrderModel).where(OrderModel.order_id == order_id).options(selectinload(OrderModel.items))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._to_domain(model) if model else None
    
    async def get_by_customer(self, customer_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Obtiene todas las órdenes de un cliente."""
        stmt = select(OrderModel).where(OrderModel.customer_id == customer_id).options(selectinload(OrderModel.items)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Obtiene todas las órdenes con paginación."""
        stmt = select(OrderModel).options(selectinload(OrderModel.items)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    async def delete(self, order_id: UUID) -> bool:
        """Elimina una orden por su ID."""
        stmt = select(OrderModel).where(OrderModel.order_id == order_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.flush()
        return True
