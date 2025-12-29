"""
Manejadores de eventos para el módulo de Pedidos.
"""
from loguru import logger
from src.modules.pedidos.domain.events import OrderCreatedEvent
from src.core.events.event_bus import EventBus


async def handle_order_created_notification(event: OrderCreatedEvent):
    """
    Simula el envío de una notificación (Email/Push) cuando se crea una orden.
    """
    logger.info(f"--- [NOTIFICACIÓN] ---")
    logger.info(f"Nuevo pedido recibido: {event.order_id}")
    logger.info(f"Cliente: {event.customer_id}")
    logger.info(f"Monto Total: ${event.total_amount}")
    logger.info(f"Items: {event.items_count}")
    logger.info(f"----------------------")


def register_order_handlers():
    """Registra los manejadores del módulo de Pedidos en el EventBus."""
    EventBus.subscribe(OrderCreatedEvent, handle_order_created_notification)
