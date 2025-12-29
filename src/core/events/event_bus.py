"""
Infraestructura base para Eventos de Dominio.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Type, Callable, Coroutine, Any
import uuid
import asyncio
from loguru import logger


@dataclass(kw_only=True)
class DomainEvent:
    """Clase base para todos los eventos de dominio."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=datetime.utcnow)



class EventBus:
    """
    Bus de eventos interno (In-memory) para comunicación desacoplada 
    entre módulos del monolito.
    """
    
    _subscribers: Dict[Type[DomainEvent], List[Callable[[Any], Coroutine[Any, Any, None]]]] = {}

    @classmethod
    def subscribe(cls, event_type: Type[DomainEvent], handler: Callable[[Any], Coroutine[Any, Any, None]]):
        """Registra un suscriptor para un tipo de evento."""
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(handler)
        logger.debug(f"Suscrito handler {handler.__name__} al evento {event_type.__name__}")

    @classmethod
    async def publish(cls, events: List[DomainEvent]):
        """Publica una lista de eventos a todos los suscriptores interesados."""
        for event in events:
            event_type = type(event)
            if event_type in cls._subscribers:
                handlers = cls._subscribers[event_type]
                # Ejecutar handlers de forma asíncrona
                tasks = [handler(event) for handler in handlers]
                await asyncio.gather(*tasks)
                logger.info(f"Evento {event_type.__name__} publicado a {len(handlers)} handlers")
            else:
                logger.debug(f"Saliendo sin publicar: No hay suscriptores para {event_type.__name__}")
