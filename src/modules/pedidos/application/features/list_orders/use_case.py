"""
Caso de uso para listar órdenes.
"""
from typing import List

from src.modules.pedidos.domain.repositories import OrderRepository
from src.modules.pedidos.application.features.place_order.response import PlaceOrderResponse, OrderItemResponse


class ListOrdersUseCase:
    """
    Caso de uso: Listar Órdenes.
    Obtiene una lista paginada de órdenes del repositorio.
    """
    
    def __init__(self, repository: OrderRepository):
        self.repository = repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[PlaceOrderResponse]:
        """
        Ejecuta la lógica de negocio.
        
        Args:
            skip: Cantidad de registros a saltar
            limit: Cantidad máxima de registros a retornar
            
        Returns:
            Lista de DTOs de órdenes
        """
        # Obtener entidades del dominio
        orders = await self.repository.get_all(skip, limit)
        
        # Convertir a DTOs de respuesta
        return [
            PlaceOrderResponse(
                order_id=o.order_id,
                customer_id=o.customer_info.customer_id,
                customer_name=o.customer_info.name,
                items=[
                    OrderItemResponse(
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity.value,
                        unit_price=item.unit_price,
                        subtotal=item.calculate_subtotal()
                    )
                    for item in o.items
                ],
                total_amount=o.total_amount,
                status=o.status.value,
                created_at=o.created_at
            )
            for o in orders
        ]
