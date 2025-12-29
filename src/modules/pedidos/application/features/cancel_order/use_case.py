"""
Caso de Uso: Cancelar Orden.
Este use case cancela una orden y libera automáticamente el stock reservado.
"""
from datetime import datetime
from loguru import logger

from src.modules.pedidos.application.features.cancel_order.command import CancelOrderCommand
from src.modules.pedidos.application.features.cancel_order.response import CancelOrderResponse
from src.modules.pedidos.domain.repositories import OrderRepository
from src.modules.pedidos.domain.gateways import InventoryGateway
from src.core.exceptions import NotFoundError, BusinessRuleViolation


class CancelOrderUseCase:
    """
    Caso de Uso: Cancelar una orden.
    
    Este use case es crítico para la integridad del inventario.
    Cuando se cancela una orden, debe liberar automáticamente el stock
    que había sido reservado.
    
    Responsabilidades:
    1. Verificar que la orden exista
    2. Validar que la orden pueda cancelarse (reglas de negocio)
    3. Cancelar la orden (cambiar estado)
    4. Liberar el stock reservado (llamar al gateway de inventario)
    5. Actualizar la orden en la base de datos
    """
    
    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_gateway: InventoryGateway
    ):
        """
        Constructor con Inyección de Dependencias.
        
        Args:
            order_repository: Implementación del puerto OrderRepository
            inventory_gateway: Gateway para comunicación con el módulo de Catálogo
        """
        self.order_repository = order_repository
        self.inventory_gateway = inventory_gateway
    
    async def execute(self, command: CancelOrderCommand) -> CancelOrderResponse:
        """
        Ejecuta el caso de uso.
        
        Args:
            command: Datos de entrada con el ID de la orden y razón de cancelación
            
        Returns:
            CancelOrderResponse con el resultado de la cancelación
            
        Raises:
            NotFoundError: Si la orden no existe
            BusinessRuleViolation: Si la orden no puede cancelarse
        """
        logger.info(f"Iniciando cancelación de orden {command.order_id}")
        # Fase 1: Obtener la orden
        order = await self.order_repository.get_by_id(command.order_id)
        
        if not order:
            raise NotFoundError("Order", str(command.order_id))
        
        # Fase 2: Cancelar la orden (esto valida las reglas de negocio)
        # La entidad Order tiene la lógica de negocio para validar si puede cancelarse
        order.cancel(reason=command.reason)
        
        # Fase 3: Liberar el stock reservado
        stock_released = False
        try:
            logger.debug(f"Liberando stock para {len(order.items)} items")
            stock_released = await self.inventory_gateway.release_stock(order.items)
            logger.info("Stock liberado correctamente")
        except Exception as e:
            logger.error(f"Fallo al liberar stock para orden {order.order_id}: {str(e)}")
            # Si falla la liberación de stock, revertir la cancelación
            # En una implementación con Unit of Work, esto sería automático
            raise BusinessRuleViolation(
                f"No se pudo liberar el stock: {str(e)}. La orden no fue cancelada."
            )
        
        # Fase 4: Actualizar la orden en la base de datos
        updated_order = await self.order_repository.update(order)
        logger.info(f"Orden {updated_order.order_id} cancelada exitosamente")
        
        return CancelOrderResponse(
            order_id=updated_order.order_id,
            status=updated_order.status.value,
            cancelled_at=updated_order.updated_at,
            reason=command.reason or "Sin razón especificada",
            stock_released=stock_released,
            message=f"Orden {updated_order.order_id} cancelada exitosamente"
        )
