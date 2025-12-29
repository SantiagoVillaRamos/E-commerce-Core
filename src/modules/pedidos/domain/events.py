"""
Evento de dominio: Orden Creada.
"""
from dataclasses import dataclass
from uuid import UUID
from typing import List

from src.core.events.event_bus import DomainEvent


@dataclass(kw_only=True)
class OrderCreatedEvent(DomainEvent):
    """
    Evento que notifica la creación de un nuevo pedido.
    """
    order_id: UUID
    customer_id: str
    total_amount: float
    items_count: int
