"""
Exception Handlers globales para FastAPI.
Centraliza el manejo de excepciones de toda la aplicación.
"""
import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import (
    DomainError,
    ValidationError,
    BusinessRuleViolation,
    NotFoundError,
    InfrastructureError,
    AuthorizationError
)

# Logger centralizado
logger = logging.getLogger(__name__)


class ErrorResponse:
    """
    Estructura estandarizada de respuestas de error.
    """
    
    @staticmethod
    def create(
        error_type: str,
        message: str,
        code: str,
        status_code: int,
        context: dict = None,
        request_id: str = None
    ) -> dict:
        """Crea una respuesta de error estandarizada."""
        response = {
            "success": False,
            "error": {
                "type": error_type,
                "code": code,
                "message": message,
            }
        }
        
        if context:
            response["error"]["context"] = context
        
        if request_id:
            response["request_id"] = request_id
        
        return response


# ==================== Domain Exception Handlers ====================

async def validation_error_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    Handler para errores de validación de dominio.
    
    Ejemplos: SKU inválido, precio negativo, etc.
    """
    logger.warning(
        f"Validation error: {exc.message}",
        extra={
            "error_code": exc.code,
            "context": exc.context,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse.create(
            error_type="ValidationError",
            message=exc.message,
            code=exc.code,
            status_code=400,
            context=exc.context
        )
    )


async def business_rule_violation_handler(
    request: Request,
    exc: BusinessRuleViolation
) -> JSONResponse:
    """
    Handler para violaciones de reglas de negocio.
    
    Ejemplos: SKU duplicado, stock insuficiente, etc.
    """
    logger.warning(
        f"Business rule violation: {exc.message}",
        extra={
            "error_code": exc.code,
            "context": exc.context,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.create(
            error_type="BusinessRuleViolation",
            message=exc.message,
            code=exc.code,
            status_code=422,
            context=exc.context
        )
    )


async def not_found_error_handler(
    request: Request,
    exc: NotFoundError
) -> JSONResponse:
    """
    Handler para entidades no encontradas.
    """
    logger.info(
        f"Entity not found: {exc.entity_name} with ID {exc.entity_id}",
        extra={
            "error_code": exc.code,
            "context": exc.context,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse.create(
            error_type="NotFoundError",
            message=exc.message,
            code=exc.code,
            status_code=404,
            context=exc.context
        )
    )


async def infrastructure_error_handler(
    request: Request,
    exc: InfrastructureError
) -> JSONResponse:
    """
    Handler para errores de infraestructura.
    """
    logger.error(
        f"Infrastructure error: {exc.message}",
        extra={
            "error_code": exc.code,
            "context": exc.context,
            "path": request.url.path
        },
        exc_info=True  # Incluye stack trace
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse.create(
            error_type="InfrastructureError",
            message="Servicio temporalmente no disponible",
            code=exc.code,
            status_code=503
        )
    )


async def authorization_error_handler(
    request: Request,
    exc: AuthorizationError
) -> JSONResponse:
    """
    Handler para errores de autorización.
    """
    logger.warning(
        f"Authorization error: {exc.message}",
        extra={
            "error_code": exc.code,
            "context": exc.context,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ErrorResponse.create(
            error_type="AuthorizationError",
            message=exc.message,
            code=exc.code,
            status_code=403
        )
    )


async def domain_error_handler(
    request: Request,
    exc: DomainError
) -> JSONResponse:
    """
    Handler genérico para errores de dominio.
    """
    logger.error(
        f"Domain error: {exc.message}",
        extra={
            "error_code": exc.code,
            "context": exc.context,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse.create(
            error_type="DomainError",
            message=exc.message,
            code=exc.code,
            status_code=400,
            context=exc.context
        )
    )


# ==================== FastAPI/Pydantic Exception Handlers ====================

async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para errores de validación de Pydantic (request body).
    """
    logger.warning(
        f"Request validation error: {exc.errors()}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.create(
            error_type="RequestValidationError",
            message="Datos de entrada inválidos",
            code="INVALID_REQUEST_DATA",
            status_code=422,
            context={"errors": exc.errors()}
        )
    )


# ==================== Generic Exception Handler ====================

async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handler para excepciones no manejadas.
    """
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.create(
            error_type="InternalServerError",
            message="Error interno del servidor",
            code="INTERNAL_SERVER_ERROR",
            status_code=500
        )
    )


# ==================== Función de Registro ====================

def register_exception_handlers(app):
    """
    Registra todos los exception handlers en la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    # Domain exceptions (orden específico a genérico)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(BusinessRuleViolation, business_rule_violation_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(InfrastructureError, infrastructure_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
    
    # FastAPI/Pydantic exceptions
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    
    # Generic exception (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered successfully")
