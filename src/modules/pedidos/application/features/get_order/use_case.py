"""
Caso de Uso: Obtener Orden.
"""
from src.modules.pedidos.application.features.get_order.command import GetOrderCommand
from src.modules.pedidos.application.features.get_order.response import GetOrderResponse, OrderItemResponse
from src.modules.pedidos.domain.repositories import OrderRepository
from src.core.exceptions import NotFoundError

class GetOrderUseCase:
    """
    Caso de Uso: Obtener los detalles de una orden por su ID.
    """
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
        
    async def execute(self, command: GetOrderCommand) -> GetOrderResponse:
        """
        Busca la orden en el repositorio y la retorna como DTO.
        """
        order = await self.order_repository.get_by_id(command.order_id)
        if not order:
            raise NotFoundError("Order", str(command.order_id))
            
        return GetOrderResponse(
            order_id=order.order_id,
            customer_id=order.customer_info.customer_id,
            customer_name=order.customer_info.name,
            customer_email=order.customer_info.email,
            customer_phone=order.customer_info.phone,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity.value,
                    unit_price=item.unit_price,
                    subtotal=item.calculate_subtotal()
                )
                for item in order.items
            ],
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            confirmed_at=order.confirmed_at,
            cancelled_at=order.cancelled_at
        )
