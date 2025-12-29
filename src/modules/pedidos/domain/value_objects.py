"""
Value Objects del dominio de Pedidos.
"""
from dataclasses import dataclass
from enum import Enum
import re
from src.core.exceptions import ValidationError


class OrderStatus(str, Enum):
    """
    Estado de una orden.
    Representa el ciclo de vida de un pedido.
    """
    PENDING = "pending"           # Orden creada, esperando confirmación
    CONFIRMED = "confirmed"       # Orden confirmada, stock reservado
    PROCESSING = "processing"     # En proceso de preparación
    SHIPPED = "shipped"           # Enviada
    DELIVERED = "delivered"       # Entregada
    CANCELLED = "cancelled"       # Cancelada
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Quantity:
    """
    Cantidad de productos en un pedido.
    Reglas:
    - Debe ser mayor que 0
    - Debe ser un número entero
    """
    value: int
    
    MAX_PER_ITEM = 100
    
    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValidationError("La cantidad debe ser un número entero")
        
        if self.value <= 0:
            raise ValidationError("La cantidad debe ser mayor que 0")
            
        if self.value > self.MAX_PER_ITEM:
            raise ValidationError(f"La cantidad por item no puede exceder {self.MAX_PER_ITEM}")
    
    def __int__(self) -> int:
        return self.value
    
    def __mul__(self, price: float) -> float:
        """Multiplica cantidad por precio."""
        return self.value * price


@dataclass(frozen=True)
class Address:
    """
    Dirección de envío.
    Reglas:
    - Todos los campos son obligatorios
    """
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "Colombia"
    
    def __post_init__(self):
        if not self.street or len(self.street) < 5:
            raise ValidationError("La calle debe tener al menos 5 caracteres")
        
        if not self.city or len(self.city) < 2:
            raise ValidationError("La ciudad debe tener al menos 2 caracteres")
        
        if not self.state:
            raise ValidationError("El estado/departamento es obligatorio")
        
        if not self.postal_code:
            raise ValidationError("El código postal es obligatorio")
        
        if not self.country:
            raise ValidationError("El país es obligatorio")
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"


@dataclass(frozen=True)
class CustomerInfo:
    """
    Información del cliente.
    """
    customer_id: str
    name: str
    email: str
    phone: str
    
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX = r'^\+?[0-9]{7,15}$'  # Básico: 7 a 15 dígitos, opcional + al inicio
    
    def __post_init__(self):
        if not self.customer_id:
            raise ValidationError("El ID del cliente es obligatorio")
        
        if not self.name or len(self.name) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres")
        
        if not self.email or not re.match(self.EMAIL_REGEX, self.email):
            raise ValidationError("El email debe ser válido")
        
        if not self.phone or not re.match(self.PHONE_REGEX, self.phone):
            raise ValidationError("El teléfono debe ser válido (7-15 dígitos)")
