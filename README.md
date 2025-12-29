# E-commerce Core

Sistema de gestión de comercio electrónico construido con **Monolito Modular**, **Vertical Slicing** y **Clean Architecture/DDD**.

## 🏗️ Arquitectura

- **Monolito Modular**: Módulos independientes con límites claros (Catálogo, Pedidos, Usuarios)
- **Vertical Slicing**: Cada feature implementa todas las capas (Domain → Application → Infrastructure → API)
- **Clean Architecture + DDD**: Separación de capas con el dominio como núcleo

## 📁 Estructura del Proyecto

```
src/
├── core/                    # Infraestructura compartida
│   ├── config.py           # Configuración
│   ├── database.py         # SQLAlchemy setup
│   ├── exceptions.py       # Excepciones base
│   └── container.py        # DI Container
│
├── modules/                 # Módulos del monolito
│   └── catalogo/           # Módulo de Catálogo
│       ├── domain/         # Capa de Dominio (Entidades, VOs, Puertos)
│       ├── application/    # Capa de Aplicación (Use Cases, Commands)
│       ├── infrastructure/ # Capa de Infraestructura (Repositorios, DB)
│       └── api/            # Capa de API (Routers, Endpoints)
│
├── scripts/                # Scripts de utilidad
└── main.py                 # Punto de entrada FastAPI
```

## 🚀 Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia `.env.example` a `.env` y configura tu base de datos:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
```

### 4. Inicializar base de datos

El proyecto usa **Alembic** para gestión de migraciones de base de datos.

#### Opción A: Usar Alembic (Recomendado)

```bash
# Aplicar todas las migraciones
alembic upgrade head

# Ver estado actual
alembic current

# Ver historial de migraciones
alembic history
```

#### Opción B: Script legacy (solo desarrollo)

```bash
python -m src.scripts.init_db
```

> [!WARNING]
> El script `init_db.py` es legacy y solo debe usarse en desarrollo local.
> En producción, siempre usa Alembic para gestionar el esquema.


## 🏃 Ejecutar la aplicación

```bash
python -m src.main
```

O usando uvicorn directamente:

```bash
uvicorn src.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Endpoints Disponibles

### Catálogo

- `POST /api/v1/catalogo/products` - Crear producto
- `GET /api/v1/catalogo/products` - Listar productos
- `GET /api/v1/catalogo/health` - Health check

### Pedidos

- `POST /api/v1/pedidos/orders` - Crear orden (reserva stock automáticamente)
- `GET /api/v1/pedidos/orders` - Listar órdenes
- `GET /api/v1/pedidos/health` - Health check

## 🎯 Ejemplo de Uso

### Crear un producto

```bash
curl -X POST "http://localhost:8000/api/v1/catalogo/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "LAPTOP-001",
    "name": "Laptop Dell XPS 15",
    "description": "Laptop de alto rendimiento",
    "price": 1299.99,
    "currency": "USD",
    "initial_stock": 10
  }'
```

### Crear una orden (demuestra comunicación entre módulos)

```bash
curl -X POST "http://localhost:8000/api/v1/pedidos/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_info": {
      "customer_id": "CUST-001",
      "name": "Juan Pérez",
      "email": "juan@example.com",
      "phone": "+57 300 1234567"
    },
    "items": [
      {
        "product_id": "<ID_DEL_PRODUCTO_CREADO>",
        "quantity": 2
      }
    ],
    "shipping_address": {
      "street": "Calle 123 #45-67",
      "city": "Bogotá",
      "state": "Cundinamarca",
      "postal_code": "110111",
      "country": "Colombia"
    }
  }'
```

> [!IMPORTANT]
> Al crear una orden, el sistema automáticamente:
> 1. Verifica que los productos existan
> 2. Valida que haya stock suficiente
> 3. Reserva el stock (reduce la cantidad disponible)
> 4. Crea y confirma la orden
> 
> Esto demuestra la **comunicación entre módulos** usando el patrón Gateway.

## 🧩 Módulos Implementados

- ✅ **Catálogo**: Gestión de productos con reserva de stock
- ✅ **Pedidos**: Gestión de órdenes con comunicación al Catálogo
- 🚧 **Usuarios**: Gestión de usuarios (próximamente)

## 📖 Conceptos DDD Aplicados

### Módulo Catálogo
- **Value Objects**: `SKU`, `Price`, `Stock`
- **Entities**: `Product`
- **Aggregates**: `Product` (raíz)
- **Repository Ports**: `ProductRepository`
- **Use Cases**: `CreateProductUseCase`, `ReserveStockUseCase`

### Módulo Pedidos
- **Value Objects**: `OrderStatus`, `Quantity`, `Address`, `CustomerInfo`
- **Entities**: `Order` (raíz), `OrderItem`
- **Aggregates**: `Order` (raíz)
- **Repository Ports**: `OrderRepository`
- **Gateway Ports**: `InventoryGateway` (comunicación con Catálogo)
- **Use Cases**: `PlaceOrderUseCase`

### Comunicación entre Módulos
- **Gateway Pattern**: `CatalogoInventoryGateway` conecta Pedidos → Catálogo
- **Bounded Contexts**: Cada módulo es un contexto delimitado independiente
- **Anti-Corruption Layer**: El Gateway protege el dominio de Pedidos

## 🔄 Migraciones de Base de Datos

El proyecto usa **Alembic** para gestión profesional del esquema de base de datos.

### Comandos Principales

```bash
# Ver estado actual de migraciones
alembic current

# Ver historial de migraciones
alembic history --verbose

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar una migración específica
alembic upgrade <revision>

# Revertir una migración
alembic downgrade -1

# Revertir a una revisión específica
alembic downgrade <revision>

# Generar nueva migración automáticamente
alembic revision --autogenerate -m "descripción del cambio"

# Crear migración vacía
alembic revision -m "descripción del cambio"
```

### Estructura de Migraciones

```
alembic/
├── versions/           # Scripts de migración
│   └── 001_initial_schema.py
├── env.py             # Configuración de entorno (async)
└── script.py.mako     # Template para nuevas migraciones
```

### Migraciones Incluidas

1. **001_initial_schema**: Esquema inicial con tablas `products`, `orders`, `order_items`
   - Incluye campos `version` para control de concurrencia optimista
   - Índices en `sku` y `customer_id`

> [!IMPORTANT]
> Siempre revisa las migraciones generadas automáticamente antes de aplicarlas.
> Alembic puede no detectar todos los cambios correctamente.

## 🛠️ Stack Tecnológico


- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Testing**: Pytest

