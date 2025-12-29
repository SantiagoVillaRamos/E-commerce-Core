import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
class TestCatalogoAPI:
    """Tests de integración para la API de Catálogo."""
    
    async def test_create_product(self, client: AsyncClient):
        """Prueba la creación de un producto."""
        payload = {
            "sku": "TEST-SKU-001",
            "name": "Test Product",
            "description": "A description for testing",
            "price": 100.50,
            "currency": "USD",
            "initial_stock": 50
        }
        
        response = await client.post("/api/v1/catalogo/products", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "TEST-SKU-001"
        assert data["name"] == "Test Product"
        assert "product_id" in data
        return data["product_id"]

    async def test_get_product_by_id(self, client: AsyncClient):
        """Prueba obtener un producto por su ID."""
        # 1. Crear producto primero
        create_payload = {
            "sku": "TEST-SKU-002",
            "name": "Get Me By ID",
            "description": "Desc",
            "price": 50.0,
            "initial_stock": 10
        }
        create_res = await client.post("/api/v1/catalogo/products", json=create_payload)
        product_id = create_res.json()["product_id"]
        
        # 2. Consultar por ID
        response = await client.get(f"/api/v1/catalogo/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product_id
        assert data["sku"] == "TEST-SKU-002"

    async def test_list_products(self, client: AsyncClient):
        """Prueba listar productos."""
        # Crear un producto para asegurar que hay al menos uno
        await client.post("/api/v1/catalogo/products", json={
            "sku": "LIST-001",
            "name": "Listable",
            "price": 10.0,
            "initial_stock": 5
        })
        
        response = await client.get("/api/v1/catalogo/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    async def test_update_product(self, client: AsyncClient):
        """Prueba actualizar un producto."""
        # 1. Crear
        create_res = await client.post("/api/v1/catalogo/products", json={
            "sku": "UP-001",
            "name": "To Update",
            "price": 100.0,
            "initial_stock": 5
        })
        product_id = create_res.json()["product_id"]
        
        # 2. Actualizar
        update_payload = {
            "product_id": product_id,
            "name": "Updated Name",
            "price": 120.0
        }
        response = await client.put(f"/api/v1/catalogo/products/{product_id}", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 120.0

    async def test_delete_product_logical(self, client: AsyncClient):
        """Prueba desactivación lógica."""
        # 1. Crear
        create_res = await client.post("/api/v1/catalogo/products", json={
            "sku": "DEL-001",
            "name": "To Delete",
            "price": 10.0,
            "initial_stock": 5
        })
        product_id = create_res.json()["product_id"]
        
        # 2. Borrar (lógico por defecto)
        response = await client.delete(f"/api/v1/catalogo/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 3. Verificar que sigue ahí pero inactivo (si implementamos lógica de inactividad en get)
        # Por ahora solo verificamos el mensaje
        assert "desactivado exitosamente" in response.json()["message"]

    async def test_create_product_duplicate_sku(self, client: AsyncClient):
        """Prueba error al crear SKU duplicado."""
        payload = {
            "sku": "DUPE-001",
            "name": "Original",
            "price": 10.0,
            "initial_stock": 5
        }
        await client.post("/api/v1/catalogo/products", json=payload)
        
        # Intentar crear con mismo SKU
        response = await client.post("/api/v1/catalogo/products", json=payload)
        assert response.status_code == 422
        assert "ya existe" in response.json()["error"]["message"].lower()
