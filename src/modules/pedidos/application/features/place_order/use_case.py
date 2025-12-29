"""
Caso de Uso: Crear Orden (Place Order).
Orquesta la lógica de aplicación para crear una orden.
"""
from typing import List
from loguru import logger
from src.modules.pedidos.application.features.place_order.command import PlaceOrderCommand
from src.modules.pedidos.application.features.place_order.response import (
    PlaceOrderResponse, OrderItemResponse
)
from src.modules.pedidos.domain.entities import Order, OrderItem
from src.modules.pedidos.domain.value_objects import (
    Quantity, Address, CustomerInfo
)
from src.modules.pedidos.domain.repositories import OrderRepository
from src.modules.pedidos.domain.gateways import InventoryGateway, StockReservationError
from src.core.exceptions import BusinessRuleViolation, NotFoundError


class PlaceOrderUseCase:
    """
    Caso de Uso: Crear una nueva orden.
    
    Este es el caso de uso CLAVE que demuestra la comunicación entre módulos.
    
    Responsabilidades:
    1. Obtener información de productos del catálogo (via Gateway)
    2. Verificar y reservar stock (via Gateway) 
    3. Crear la entidad Order con los items
    4. Confirmar la orden
    5. Persistir usando el repositorio
    """
    
    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_gateway: InventoryGateway
    ):
        """
        Constructor con Inyección de Dependencias.
        
        Args:
            order_repository: Implementación del puerto OrderRepository
            inventory_gateway: Implementación del puerto InventoryGateway
        """
        self.order_repository = order_repository
        self.inventory_gateway = inventory_gateway
    
    async def execute(self, command: PlaceOrderCommand) -> PlaceOrderResponse:
        """
        Ejecuta el caso de uso.
        
        Args:
            command: Datos de entrada para crear la orden
            
        Returns:
            PlaceOrderResponse con los datos de la orden creada
            
        Raises:
            BusinessRuleViolation: Si hay violaciones de reglas de negocio
            StockReservationError: Si no hay stock suficiente
            NotFoundError: Si algún producto no existe
        """
        logger.info(f"Iniciando proceso de creación de orden para cliente {command.customer_info.customer_id}")
        
        # 1. Crear Value Objects
        customer_info = CustomerInfo(
            customer_id=command.customer_info.customer_id,
            name=command.customer_info.name,
            email=command.customer_info.email,
            phone=command.customer_info.phone
        )
        
        shipping_address = Address(
            street=command.shipping_address.street,
            city=command.shipping_address.city,
            state=command.shipping_address.state,
            postal_code=command.shipping_address.postal_code,
            country=command.shipping_address.country
        )
        
        # 2. Crear items preliminares (necesitamos obtener precios del catálogo)
        # NOTA: En una implementación real, obtendríamos los precios del Gateway
        # Por ahora, usaremos un precio dummy que será reemplazado por el adaptador
        order_items: List[OrderItem] = []
        
        for item_cmd in command.items:
            # Verificar que el producto existe
            exists = await self.inventory_gateway.verify_product_exists(item_cmd.product_id)
            if not exists:
                raise NotFoundError("Product", str(item_cmd.product_id))
            
            # Crear OrderItem (el precio será obtenido por el Gateway en el paso siguiente)
            # Por ahora usamos un placeholder
            order_item = OrderItem(
                product_id=item_cmd.product_id,
                product_name="",  # Será llenado por el Gateway
                quantity=Quantity(value=item_cmd.quantity),
                unit_price=0.0  # Será llenado por el Gateway
            )
            order_items.append(order_item)
        
        # 3. PASO CRUCIAL: Verificar y reservar stock (comunicación con Catálogo)
        try:
            logger.debug(f"Verificando y reservando stock para {len(order_items)} items")
            await self.inventory_gateway.verify_and_reserve_stock(order_items)
            logger.info("Stock reservado exitosamente")
        except StockReservationError as e:
            logger.error(f"Error al reservar stock: {e.message}")
            raise BusinessRuleViolation(f"No se pudo reservar el stock: {e.message}")
        
        # 4. Crear la entidad Order
        order = Order(
            customer_info=customer_info,
            items=order_items,
            shipping_address=shipping_address
        )
        
        # 5. Confirmar la orden (cambia estado a CONFIRMED)
        order.confirm()
        
        # 6. Persistir la orden
        saved_order = await self.order_repository.save(order)
        logger.info(f"Orden {saved_order.order_id} creada exitosamente con estado {saved_order.status}")
        
        # 7. Mapear a Response DTO
        items_response = [
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity.value,
                unit_price=item.unit_price,
                subtotal=item.calculate_subtotal()
            )
            for item in saved_order.items
        ]
        
        return PlaceOrderResponse(
            order_id=saved_order.order_id,
            customer_id=saved_order.customer_info.customer_id,
            customer_name=saved_order.customer_info.name,
            items=items_response,
            total_amount=saved_order.total_amount,
            status=saved_order.status.value,
            created_at=saved_order.created_at
        )
