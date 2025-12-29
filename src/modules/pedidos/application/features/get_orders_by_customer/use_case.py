"""
Caso de Uso: Obtener Órdenes por Cliente.
"""
from src.modules.pedidos.application.features.get_orders_by_customer.command import GetOrdersByCustomerCommand
from src.modules.pedidos.application.features.get_orders_by_customer.response import GetOrdersByCustomerResponse
from src.modules.pedidos.application.features.get_order.response import GetOrderResponse, OrderItemResponse
from src.modules.pedidos.domain.repositories import OrderRepository

class GetOrdersByCustomerUseCase:
    """
    Caso de Uso: Obtener todas las órdenes asociadas a un ID de cliente.
    """
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
        
    async def execute(self, command: GetOrdersByCustomerCommand) -> GetOrdersByCustomerResponse:
        """
        Busca las órdenes en el repositorio.
        """
        orders = await self.order_repository.get_by_customer(
            command.customer_id, 
            command.skip, 
            command.limit
        )
        
        # Mapear a lista de DTOs
        order_dtos = [
            GetOrderResponse(
                order_id=o.order_id,
                customer_id=o.customer_info.customer_id,
                customer_name=o.customer_info.name,
                customer_email=o.customer_info.email,
                customer_phone=o.customer_info.phone,
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
                created_at=o.created_at,
                confirmed_at=o.confirmed_at,
                cancelled_at=o.cancelled_at
            )
            for o in orders
        ]
        
        return GetOrdersByCustomerResponse(
            customer_id=command.customer_id,
            orders=order_dtos,
            total=len(order_dtos)
        )
