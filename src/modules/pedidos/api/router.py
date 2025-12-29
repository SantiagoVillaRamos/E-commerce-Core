"""
Router de FastAPI para el módulo de Pedidos.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.modules.pedidos.application.features.place_order.command import PlaceOrderCommand
from src.modules.pedidos.application.features.place_order.response import PlaceOrderResponse
from src.modules.pedidos.application.features.place_order.use_case import PlaceOrderUseCase
from src.modules.pedidos.application.features.cancel_order.command import CancelOrderCommand
from src.modules.pedidos.application.features.cancel_order.response import CancelOrderResponse
from src.modules.pedidos.application.features.cancel_order.use_case import CancelOrderUseCase
from src.modules.pedidos.application.features.list_orders.use_case import ListOrdersUseCase
from src.modules.pedidos.api.dependencies import get_place_order_use_case, get_list_orders_use_case, get_cancel_order_use_case
from src.modules.pedidos.domain.gateways import StockReservationError
from src.core.exceptions import DomainError, BusinessRuleViolation, ValidationError, NotFoundError



# Router del módulo
router = APIRouter()


@router.post(
    "/orders",
    response_model=PlaceOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva orden",
    description="Crea una nueva orden verificando y reservando stock del catálogo"
)
async def place_order(
    command: PlaceOrderCommand,
    use_case: PlaceOrderUseCase = Depends(get_place_order_use_case)
) -> PlaceOrderResponse:
    """
    Endpoint para crear una nueva orden.
    
    Este endpoint demuestra la comunicación entre módulos:
    1. Recibe la orden del cliente
    2. Verifica stock en el módulo de Catálogo (via Gateway)
    3. Reserva el stock
    4. Crea y confirma la orden
    
    Args:
        command: Datos de la orden a crear
        use_case: Caso de uso inyectado automáticamente
        
    Returns:
        Datos de la orden creada
        
    Raises:
        HTTPException 400: Si hay errores de validación o reglas de negocio
        HTTPException 404: Si algún producto no existe
        HTTPException 500: Si hay errores internos
    """
    try:
        # Ejecutar el caso de uso
        result = await use_case.execute(command)
        return result
        
    except NotFoundError as e:
        # Producto no encontrado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "message": e.message}
        )
        
    except StockReservationError as e:
        # Error al reservar stock (stock insuficiente, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Stock Reservation Error", "message": e.message}
        )
        
    except ValidationError as e:
        # Errores de validación de dominio
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Validation Error", "message": e.message}
        )
        
    except BusinessRuleViolation as e:
        # Violaciones de reglas de negocio
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business Rule Violation", "message": e.message}
        )
        
    except DomainError as e:
        # Otros errores de dominio
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Domain Error", "message": e.message}
        )
        
    except Exception as e:
        # Errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal Server Error", "message": str(e)}
        )


@router.get(
    "/orders",
    response_model=List[PlaceOrderResponse],
    summary="Listar órdenes",
    description="Obtiene una lista paginada de órdenes"
)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    use_case: ListOrdersUseCase = Depends(get_list_orders_use_case)
) -> List[PlaceOrderResponse]:
    """
    Endpoint para listar órdenes.
    """
    return await use_case.execute(skip, limit)


@router.post(
    "/orders/{order_id}/cancel",
    response_model=CancelOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancelar una orden",
    description="Cancela una orden existente y libera el stock reservado"
)
async def cancel_order(
    order_id: str,
    reason: str = None,
    use_case: CancelOrderUseCase = Depends(get_cancel_order_use_case)
) -> CancelOrderResponse:
    """
    Endpoint para cancelar una orden.
    
    Este endpoint demuestra la comunicación entre módulos:
    1. Cancela la orden (valida reglas de negocio)
    2. Libera el stock en el módulo de Catálogo (via Gateway)
    3. Actualiza la orden
    
    Args:
        order_id: ID de la orden a cancelar
        reason: Razón de la cancelación (opcional)
        use_case: Caso de uso inyectado automáticamente
        
    Returns:
        Datos de la orden cancelada
        
    Raises:
        HTTPException 400: Si hay errores de validación o reglas de negocio
        HTTPException 404: Si la orden no existe
        HTTPException 500: Si hay errores internos
    """
    try:
        from uuid import UUID
        
        # Convertir string a UUID
        order_uuid = UUID(order_id)
        
        # Crear comando
        command = CancelOrderCommand(order_id=order_uuid, reason=reason)
        
        # Ejecutar el caso de uso
        result = await use_case.execute(command)
        return result
        
    except ValueError:
        # ID inválido
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid ID", "message": "El ID de la orden no es válido"}
        )
        
    except NotFoundError as e:
        # Orden no encontrada
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "message": e.message}
        )
        
    except StockReservationError as e:
        # Error al liberar stock
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Stock Release Error", "message": e.message}
        )
        
    except BusinessRuleViolation as e:
        # Violaciones de reglas de negocio (ej: orden ya enviada)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business Rule Violation", "message": e.message}
        )
        
    except DomainError as e:
        # Otros errores de dominio
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Domain Error", "message": e.message}
        )
        
    except Exception as e:
        # Errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal Server Error", "message": str(e)}
        )


@router.get(
    "/health",
    summary="Health check del módulo Pedidos"
)
async def health_check():
    """Endpoint de salud del módulo."""
    return {
        "module": "pedidos",
        "status": "healthy"
    }

