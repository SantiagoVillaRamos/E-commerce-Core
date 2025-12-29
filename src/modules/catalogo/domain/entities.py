"""
Entidades del dominio de Catálogo.
Las entidades tienen identidad y ciclo de vida.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.modules.catalogo.domain.value_objects import SKU, Price, Stock
from src.core.exceptions import BusinessRuleViolation


@dataclass
class Product:
    """
    Agregado Raíz: Producto.
    Representa un producto en el catálogo.
    """
    # Identidad
    product_id: UUID = field(default_factory=uuid4)
    
    # Atributos
    sku: SKU = field(default=None)
    name: str = field(default="")
    description: str = field(default="")
    price: Price = field(default=None)
    stock: Stock = field(default_factory=lambda: Stock(quantity=0))
    
    # Metadatos
    is_active: bool = field(default=True)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validaciones de la entidad."""
        if not self.name:
            raise BusinessRuleViolation("El nombre del producto no puede estar vacío")
        
        if len(self.name) < 3:
            raise BusinessRuleViolation("El nombre del producto debe tener al menos 3 caracteres")
    
    # Métodos de negocio
    
    def update_price(self, new_price: Price) -> None:
        """
        Actualiza el precio del producto.
        Regla de negocio: El precio no puede cambiar más del 50% de una vez.
        """
        if self.price:
            price_change_ratio = abs(new_price.amount - self.price.amount) / self.price.amount
            
            if price_change_ratio > 0.5:
                raise BusinessRuleViolation(
                    f"El precio no puede cambiar más del 50% de una vez. "
                    f"Cambio solicitado: {price_change_ratio * 100:.1f}%"
                )
        
        self.price = new_price
        self.updated_at = datetime.utcnow()
    
    def reserve_stock(self, quantity: int) -> None:
        """
        Reserva stock del producto.
        Regla de negocio: Solo se puede reservar si hay stock disponible.
        """
        if not self.is_active:
            raise BusinessRuleViolation(f"No se puede reservar stock de un producto inactivo: {self.name}")
        
        if not self.stock.is_available(quantity):
            raise BusinessRuleViolation(
                f"Stock insuficiente para el producto '{self.name}'. "
                f"Disponible: {self.stock.quantity}, Solicitado: {quantity}"
            )
        
        self.stock = self.stock.decrease(quantity)
        self.updated_at = datetime.utcnow()
    
    def replenish_stock(self, quantity: int) -> None:
        """Repone el stock del producto."""
        self.stock = self.stock.increase(quantity)
        self.updated_at = datetime.utcnow()
    
    def release_stock(self, quantity: int) -> None:
        """
        Libera stock previamente reservado.
        Este método se usa cuando se cancela una orden.
        
        A diferencia de replenish_stock, este método es específicamente
        para devolver stock que había sido reservado anteriormente.
        """
        self.stock = self.stock.increase(quantity)
        self.updated_at = datetime.utcnow()

    
    def deactivate(self) -> None:
        """
        Desactiva el producto.
        Regla de negocio: Un producto desactivado no puede venderse.
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activa el producto."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_details(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """Actualiza los detalles del producto."""
        if name:
            if len(name) < 3:
                raise BusinessRuleViolation("El nombre del producto debe tener al menos 3 caracteres")
            self.name = name
        
        if description is not None:
            self.description = description
        
        self.updated_at = datetime.utcnow()
