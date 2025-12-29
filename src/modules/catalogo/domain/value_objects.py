"""
Value Objects del dominio de Catálogo.
Los VOs son inmutables y encapsulan reglas de validación.
"""
from dataclasses import dataclass
from src.core.exceptions import ValidationError


@dataclass(frozen=True)
class SKU:
    """
    Stock Keeping Unit - Código único de producto.
    Reglas:
    - Debe tener al menos 5 caracteres
    - Solo alfanumérico y guiones
    """
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValidationError("SKU no puede estar vacío")
        
        if len(self.value) < 5:
            raise ValidationError("SKU debe tener al menos 5 caracteres")
        
        if not all(c.isalnum() or c == '-' for c in self.value):
            raise ValidationError("SKU solo puede contener caracteres alfanuméricos y guiones")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Price:
    """
    Precio del producto.
    Reglas:
    - Debe ser mayor que 0
    - Máximo 2 decimales
    """
    amount: float
    currency: str = "USD"
    
    MAX_PRICE = 1_000_000.0
    
    def __post_init__(self):
        if self.amount <= 0:
            raise ValidationError("El precio debe ser mayor que 0")
        
        if self.amount > self.MAX_PRICE:
            raise ValidationError(f"El precio no puede exceder {self.MAX_PRICE}")
        
        # Validar máximo 2 decimales
        if round(self.amount, 2) != self.amount:
            raise ValidationError("El precio no puede tener más de 2 decimales")
        
        if not self.currency:
            raise ValidationError("La moneda no puede estar vacía")
            
        if len(self.currency) != 3:
            raise ValidationError(f"La moneda debe tener 3 caracteres (ej. USD), recibido: '{self.currency}'")
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"
    
    def __add__(self, other: 'Price') -> 'Price':
        """Suma de precios (deben tener la misma moneda)."""
        if self.currency != other.currency:
            raise ValidationError(f"No se pueden sumar precios de diferentes monedas: {self.currency} y {other.currency}")
        
        return Price(amount=self.amount + other.amount, currency=self.currency)
    
    def __mul__(self, quantity: int) -> 'Price':
        """Multiplicación de precio por cantidad."""
        if quantity < 0:
            raise ValidationError("La cantidad no puede ser negativa")
        
        return Price(amount=round(self.amount * quantity, 2), currency=self.currency)


@dataclass(frozen=True)
class Stock:
    """
    Cantidad de stock disponible.
    Reglas:
    - No puede ser negativo
    """
    quantity: int
    
    MAX_STOCK = 100_000
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValidationError("El stock no puede ser negativo")
            
        if self.quantity > self.MAX_STOCK:
            raise ValidationError(f"El stock no puede exceder {self.MAX_STOCK}")
    
    def is_available(self, requested_quantity: int) -> bool:
        """Verifica si hay stock suficiente."""
        return self.quantity >= requested_quantity
    
    def decrease(self, amount: int) -> 'Stock':
        """Reduce el stock (retorna un nuevo Stock)."""
        if amount < 0:
            raise ValidationError("No se puede reducir el stock por una cantidad negativa")
        
        new_quantity = self.quantity - amount
        if new_quantity < 0:
            raise ValidationError(f"Stock insuficiente. Disponible: {self.quantity}, Solicitado: {amount}")
        
        return Stock(quantity=new_quantity)
    
    def increase(self, amount: int) -> 'Stock':
        """Aumenta el stock (retorna un nuevo Stock)."""
        if amount < 0:
            raise ValidationError("No se puede aumentar el stock por una cantidad negativa")
        
        return Stock(quantity=self.quantity + amount)
