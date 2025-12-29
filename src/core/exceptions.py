"""
Excepciones base del dominio con soporte para encadenamiento.
Estas excepciones son compartidas por todos los módulos.
"""
from typing import Optional, Dict, Any
from datetime import datetime


class DomainError(Exception):
    """
    Excepción base para errores de dominio.
    
    Soporta encadenamiento de excepciones y metadatos contextuales.
    """
    
    def __init__(
        self, 
        message: str,
        *,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Constructor con soporte para encadenamiento.
        
        Args:
            message: Mensaje de error legible para humanos
            code: Código de error único (ej: "INVALID_SKU", "DUPLICATE_PRODUCT")
            context: Diccionario con información contextual adicional
            cause: Excepción original que causó este error (encadenamiento)
        """
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        
        # Encadenamiento de excepciones
        super().__init__(message)
        if cause:
            self.__cause__ = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para serialización."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }


class ValidationError(DomainError):
    """
    Excepción para errores de validación de dominio.
    
    Ejemplos:
    - SKU inválido
    - Precio negativo
    - Stock negativo
    """
    
    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        value: Any = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if field:
            context['field'] = field
        if value is not None:
            context['invalid_value'] = str(value)
        
        super().__init__(message, context=context, **kwargs)


class BusinessRuleViolation(DomainError):
    """
    Excepción cuando se viola una regla de negocio.
    
    Ejemplos:
    - SKU duplicado
    - Stock insuficiente
    - Precio cambia más del 50%
    """
    
    def __init__(
        self,
        message: str,
        *,
        rule: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if rule:
            context['violated_rule'] = rule
        
        super().__init__(message, context=context, **kwargs)


class NotFoundError(DomainError):
    """
    Excepción cuando una entidad no se encuentra.
    """
    
    def __init__(
        self,
        entity_name: str,
        entity_id: str,
        **kwargs
    ):
        self.entity_name = entity_name
        self.entity_id = entity_id
        
        message = f"{entity_name} con ID '{entity_id}' no encontrado"
        context = kwargs.pop('context', {})
        context.update({
            'entity_type': entity_name,
            'entity_id': entity_id
        })
        
        super().__init__(message, context=context, **kwargs)


class InfrastructureError(DomainError):
    """
    Excepción para errores de infraestructura.
    
    Ejemplos:
    - Error de base de datos
    - Error de conexión externa
    - Error de caché
    """
    pass


class AuthorizationError(DomainError):
    """
    Excepción para errores de autorización.
    
    Ejemplos:
    - Usuario sin permisos
    - Token inválido
    """
    pass


class ConcurrencyError(DomainError):
    """
    Excepción para conflictos de concurrencia optimista.
    
    Se lanza cuando se intenta actualizar una entidad que ha sido
    modificada por otro proceso desde que fue leída.
    
    Ejemplos:
    - Actualización de producto con versión desactualizada
    - Actualización de orden con versión desactualizada
    """
    
    def __init__(
        self,
        entity_name: str,
        entity_id: str,
        expected_version: int,
        actual_version: int,
        **kwargs
    ):
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        
        message = (
            f"Conflicto de concurrencia en {entity_name} '{entity_id}'. "
            f"Versión esperada: {expected_version}, versión actual: {actual_version}. "
            f"La entidad fue modificada por otro proceso."
        )
        
        context = kwargs.pop('context', {})
        context.update({
            'entity_type': entity_name,
            'entity_id': entity_id,
            'expected_version': expected_version,
            'actual_version': actual_version
        })
        
        super().__init__(message, context=context, **kwargs)

