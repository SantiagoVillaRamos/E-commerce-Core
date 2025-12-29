"""
Caso de Uso: Actualizar Estado de Orden.
"""
from src.modules.pedidos.application.features.update_status.command import UpdateOrderStatusCommand
from src.modules.pedidos.application.features.update_status.response import UpdateOrderStatusResponse
from src.modules.pedidos.domain.repositories import OrderRepository
from src.modules.pedidos.domain.value_objects import OrderStatus
from src.core.exceptions import NotFoundError, BusinessRuleViolation

class UpdateOrderStatusUseCase:
    """
    Caso de Uso: Actualizar el estado de una orden.
    Permite avanzar la orden en su ciclo de vida.
    """
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
        
    async def execute(self, command: UpdateOrderStatusCommand) -> UpdateOrderStatusResponse:
        """
        Ejecuta la actualización del estado.
        """
        order = await self.order_repository.get_by_id(command.order_id)
        if not order:
            raise NotFoundError("Order", str(command.order_id))
            
        old_status = order.status
        try:
            new_status_enum = OrderStatus(command.new_status.lower())
        except ValueError:
            raise BusinessRuleViolation(f"Estado '{command.new_status}' no es válido")
            
        # Validaciones simples de transición
        if old_status == OrderStatus.CANCELLED:
            raise BusinessRuleViolation("No se puede cambiar el estado de una orden cancelada")
            
        if old_status == OrderStatus.DELIVERED:
            raise BusinessRuleViolation("No se puede cambiar el estado de una orden entregada")
            
        # Actualizar el estado
        order.status = new_status_enum
        
        # Guardar cambios
        await self.order_repository.update(order)
        
        return UpdateOrderStatusResponse(
            order_id=order.order_id,
            old_status=old_status.value,
            new_status=new_status_enum.value,
            success=True,
            message=f"Estado de la orden actualizado de {old_status.value} a {new_status_enum.value}"
        )
