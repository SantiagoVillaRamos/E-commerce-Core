import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
class TestPedidosAPI:
    """Tests de integración para la API de Pedidos."""
    
    async def test_place_order(self, client: AsyncClient):
        """Prueba el flujo completo de creación de una orden."""
        # 1. Necesitamos un producto en el catálogo primero
        product_payload = {
            "sku": "ORDER-TEST-001",
            "name": "Orderable Laptop",
            "price": 1000.0,
            "initial_stock": 10
        }
        prod_res = await client.post("/api/v1/catalogo/products", json=product_payload)
        product_id = prod_res.json()["product_id"]
        
        # 2. Crear la orden
        order_payload = {
            "customer_info": {
                "customer_id": "TEST-CUST-001",
                "name": "Test User",
                "email": "test@user.com",
                "phone": "12345678"
            },
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "TestCountry"
            }
        }
        
        response = await client.post("/api/v1/pedidos/orders", json=order_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == "TEST-CUST-001"
        assert len(data["items"]) == 1
        assert data["status"] == "confirmed"
        return data["order_id"]

    async def test_get_order_by_id(self, client: AsyncClient):
        """Prueba obtener una orden por su ID."""
        # 1. Create product
        prod_res = await client.post("/api/v1/catalogo/products", json={
            "sku": "GET-ORD-001", "name": "Product 1 Long Name", "price": 10.0, "initial_stock": 10
        })
        product_id = prod_res.json()["product_id"]
        
        # 2. Create order
        order_res = await client.post("/api/v1/pedidos/orders", json={
            "customer_info": {"customer_id": "C1", "name": "User Name", "email": "e@e.com", "phone": "1342345"},
            "items": [{"product_id": product_id, "quantity": 1}],
            "shipping_address": {"street": "Street 123", "city": "City Name", "state": "State", "postal_code": "12345", "country": "Country"}
        })
        order_id = order_res.json()["order_id"]
        
        # 3. Get order
        response = await client.get(f"/api/v1/pedidos/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["order_id"] == order_id

    async def test_cancel_order_releases_stock(self, client: AsyncClient):
        """Prueba que cancelar una orden libera el stock."""
        # 1. Create product with 10 units
        prod_res = await client.post("/api/v1/catalogo/products", json={
            "sku": "STOCK-001", "name": "Stock Test Product", "price": 10.0, "initial_stock": 10
        })
        product_id = prod_res.json()["product_id"]
        
        # 2. Create order for 3 units (remaining=7)
        order_res = await client.post("/api/v1/pedidos/orders", json={
            "customer_info": {"customer_id": "C2", "name": "User Two", "email": "e2@e.com", "phone": "123098123"},
            "items": [{"product_id": product_id, "quantity": 3}],
            "shipping_address": {"street": "Avenue Central 45", "city": "City Zero", "state": "S", "postal_code": "P", "country": "C"}
        })
        order_id = order_res.json()["order_id"]
        
        # Verify stock is 7
        prod_get = await client.get(f"/api/v1/catalogo/products/{product_id}")
        assert prod_get.json()["stock"] == 7
        
        # 3. Cancel order
        cancel_res = await client.post(f"/api/v1/pedidos/orders/{order_id}/cancel", json={"reason": "Test Cancellation"})
        assert cancel_res.status_code == 200
        assert cancel_res.json()["stock_released"] is True
        
        # 4. Verify stock is back to 10
        prod_get_after = await client.get(f"/api/v1/catalogo/products/{product_id}")
        assert prod_get_after.json()["stock"] == 10

    async def test_update_order_status(self, client: AsyncClient):
        """Prueba actualización de estado de orden."""
        # 1. Create order
        prod_res = await client.post("/api/v1/catalogo/products", json={
            "sku": "STATUS-001", "name": "Status Product", "price": 1.0, "initial_stock": 1
        })
        product_id = prod_res.json()["product_id"]
        order_res = await client.post("/api/v1/pedidos/orders", json={
            "customer_info": {"customer_id": "C3", "name": "User Three", "email": "e3@e.com", "phone": "1234567"},
            "items": [{"product_id": product_id, "quantity": 1}],
            "shipping_address": {"street": "Calle Principal 1", "city": "Bogota", "state": "Cundinamarca", "postal_code": "110111", "country": "Colombia"}
        })
        order_id = order_res.json()["order_id"]
        
        # 2. Update to processing
        update_payload = {
            "order_id": order_id,
            "new_status": "processing"
        }
        patch_res = await client.patch(f"/api/v1/pedidos/orders/{order_id}/status", json=update_payload)
        assert patch_res.status_code == 200
        assert patch_res.json()["new_status"] == "processing"

    async def test_get_orders_by_customer(self, client: AsyncClient):
        """Prueba obtener órdenes por cliente."""
        customer_id = "CUST-MULTI"
        # 1. Create 2 orders for same customer
        for i in range(2):
            prod_res = await client.post("/api/v1/catalogo/products", json={
                "sku": f"MULTI-{i}", "name": f"Product Multi {i}", "price": 1.0, "initial_stock": 10
            })
            product_id = prod_res.json()["product_id"]
            await client.post("/api/v1/pedidos/orders", json={
                "customer_info": {"customer_id": customer_id, "name": "Multi User", "email": "m@m.com", "phone": "123123123"},
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": {"street": "Diagonal 56 # 12-34", "city": "Medellin", "state": "Antioquia", "postal_code": "050010", "country": "Colombia"}
            })
        
        # 2. Get orders by customer
        response = await client.get(f"/api/v1/pedidos/orders/customer/{customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == customer_id
        assert len(data["orders"]) >= 2
        assert data["total"] >= 2
