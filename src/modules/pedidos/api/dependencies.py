"""
Funciones de Inyección de Dependencias para el módulo de Pedidos.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from src.core.database import get_db_session
from src.modules.pedidos.infrastructure.repositories import SQLAlchemyOrderRepository
from src.modules.pedidos.infrastructure.gateways import CatalogoInventoryGateway
from src.modules.pedidos.application.features.place_order.use_case import PlaceOrderUseCase
from src.modules.pedidos.application.features.cancel_order.use_case import CancelOrderUseCase
from src.modules.pedidos.application.features.list_orders.use_case import ListOrdersUseCase
from src.modules.pedidos.application.features.get_order.use_case import GetOrderUseCase
from src.modules.pedidos.application.features.update_status.use_case import UpdateOrderStatusUseCase
from src.modules.pedidos.application.features.get_orders_by_customer.use_case import GetOrdersByCustomerUseCase


# Dependency: Order Repository
async def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)] 
) -> SQLAlchemyOrderRepository:
    """Inyecta el repositorio de órdenes."""
    return SQLAlchemyOrderRepository(session)


# Dependency: Inventory Gateway
async def get_inventory_gateway(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CatalogoInventoryGateway:
    """
    Inyecta el Gateway de Inventario.
    
    IMPORTANTE: Este Gateway conecta con el módulo de Catálogo.
    """
    return CatalogoInventoryGateway(session)


# Dependency: PlaceOrder Use Case
async def get_place_order_use_case(
    repository: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)],
    gateway: Annotated[CatalogoInventoryGateway, Depends(get_inventory_gateway)] 
) -> PlaceOrderUseCase:
    """
    Inyecta el caso de uso PlaceOrder.
    
    Este use case recibe AMBOS: el repositorio Y el gateway.
    """
    return PlaceOrderUseCase(repository, gateway)


# Dependency: ListOrders Use Case
async def get_list_orders_use_case(
    repository: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)]
) -> "ListOrdersUseCase":
    """Inyecta el caso de uso ListOrders."""
    
    return ListOrdersUseCase(repository)


# Dependency: CancelOrder Use Case
async def get_cancel_order_use_case(
    repository: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)],
    gateway: Annotated[CatalogoInventoryGateway, Depends(get_inventory_gateway)]
) -> CancelOrderUseCase:
    """
    Inyecta el caso de uso CancelOrder.
    
    Este use case recibe AMBOS: el repositorio Y el gateway.
    El gateway es necesario para liberar el stock.
    """
    return CancelOrderUseCase(repository, gateway)


# Dependency: GetOrder Use Case
async def get_get_order_use_case(
    repository: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)]
) -> GetOrderUseCase:
    """Inyecta el caso de uso GetOrder."""
    return GetOrderUseCase(repository)


# Dependency: UpdateOrderStatus Use Case
async def get_update_status_use_case(
    repository: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)]
) -> UpdateOrderStatusUseCase:
    """Inyecta el caso de uso UpdateOrderStatus."""
    return UpdateOrderStatusUseCase(repository)


# Dependency: GetOrdersByCustomer Use Case
async def get_get_orders_by_customer_use_case(
    repository: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)]
) -> GetOrdersByCustomerUseCase:
    """Inyecta el caso de uso GetOrdersByCustomer."""
    return GetOrdersByCustomerUseCase(repository)

