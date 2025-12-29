"""
Tests unitarios para los Value Objects del dominio de Pedidos.
"""
import pytest
from src.modules.pedidos.domain.value_objects import (
    OrderStatus, Quantity, Address, CustomerInfo
)
from src.core.exceptions import ValidationError


class TestOrderStatus:
    """Tests para el enum OrderStatus."""
    
    def test_order_status_values(self):
        """Debe tener todos los estados definidos."""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PROCESSING.value == "processing"
        assert OrderStatus.SHIPPED.value == "shipped"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.CANCELLED.value == "cancelled"


class TestQuantity:
    """Tests para el Value Object Quantity."""
    
    def test_create_valid_quantity(self):
        """Debe crear una cantidad válida."""
        qty = Quantity(value=5)
        assert qty.value == 5
        assert int(qty) == 5
    
    def test_quantity_zero(self):
        """Debe rechazar cantidad cero."""
        with pytest.raises(ValidationError, match="mayor que 0"):
            Quantity(value=0)
    
    def test_quantity_negative(self):
        """Debe rechazar cantidad negativa."""
        with pytest.raises(ValidationError, match="mayor que 0"):
            Quantity(value=-5)
    
    def test_quantity_multiplication(self):
        """Debe multiplicar cantidad por precio."""
        qty = Quantity(value=3)
        result = qty * 10.50
        assert result == 31.50


class TestAddress:
    """Tests para el Value Object Address."""
    
    def test_create_valid_address(self):
        """Debe crear una dirección válida."""
        address = Address(
            street="Calle 123 #45-67",
            city="Bogotá",
            state="Cundinamarca",
            postal_code="110111",
            country="Colombia"
        )
        assert address.street == "Calle 123 #45-67"
        assert address.city == "Bogotá"
        assert "Bogotá" in str(address)
    
    def test_address_short_street(self):
        """Debe rechazar calle muy corta."""
        with pytest.raises(ValidationError, match="al menos 5 caracteres"):
            Address(
                street="ABC",
                city="Bogotá",
                state="Cundinamarca",
                postal_code="110111"
            )
    
    def test_address_empty_city(self):
        """Debe rechazar ciudad vacía."""
        with pytest.raises(ValidationError, match="al menos 2 caracteres"):
            Address(
                street="Calle 123",
                city="",
                state="Cundinamarca",
                postal_code="110111"
            )


class TestCustomerInfo:
    """Tests para el Value Object CustomerInfo."""
    
    def test_create_valid_customer_info(self):
        """Debe crear información de cliente válida."""
        info = CustomerInfo(
            customer_id="CUST-001",
            name="Juan Pérez",
            email="juan@example.com",
            phone="+573001234567"
        )
        assert info.customer_id == "CUST-001"
        assert info.name == "Juan Pérez"
    
    def test_customer_info_invalid_email(self):
        """Debe rechazar email inválido."""
        with pytest.raises(ValidationError, match="email debe ser válido"):
            CustomerInfo(
                customer_id="CUST-001",
                name="Juan Pérez",
                email="invalid-email",
                phone="+57 300 1234567"
            )
    
    def test_customer_info_short_name(self):
        """Debe rechazar nombre muy corto."""
        with pytest.raises(ValidationError, match="al menos 3 caracteres"):
            CustomerInfo(
                customer_id="CUST-001",
                name="AB",
                email="juan@example.com",
                phone="+57 300 1234567"
            )
