# Valkyria - Clothing Store Backend API

Backend completo para gestión de tienda de ropa con inventario, ventas, compras y pagos integrados con MercadoPago.

## Stack Tecnológico

| Tecnología | Uso |
|-----------|-----|
| **FastAPI** | Framework web / API REST |
| **SQLAlchemy 2.0** | ORM con Mapped columns |
| **PostgreSQL** | Base de datos relacional |
| **Alembic** | Migraciones de base de datos |
| **Pydantic v2** | Validación de datos y schemas |
| **JWT (python-jose)** | Autenticación con access tokens |
| **passlib (bcrypt)** | Hashing de contraseñas |
| **MercadoPago SDK** | Integración de pagos |
| **pytest + httpx** | Testing |

## Características

### Autenticación y Usuarios
- JWT con Bearer tokens
- Sistema de roles: `owner`, `admin`, `staff`, `customer`
- Registro público (como customer) y creación por owner (cualquier rol)
- Protección de rutas por rol

### Catálogo de Productos
- Categorías con validación de unicidad
- Productos con soft delete y variantes (talle, color, SKU)
- Precio base en producto con override opcional por variante
- Soporte de imágenes (URL)
- Búsqueda de variantes por SKU

### Inventario
- Stock en tiempo real calculado por movimientos
- Tipos de movimiento: compra, venta online, venta interna, ajuste manual
- Alertas de stock bajo (configurable por variante)
- Deducción automática al crear ventas

### Ventas
- Ventas online (clientes) e internas (staff)
- Estados: `pending` → `paid` → `preparing` → `shipped` → `completed` / `cancelled`
- Validación de stock antes de confirmar
- Multi-item con precios unitarios

### Compras a Proveedores
- CRUD de proveedores con soft delete
- Órdenes de compra con items
- Recepción parcial o total con actualización automática de inventario
- Estados: `draft` → `sent` → `partially_received` → `received`

### Pagos (MercadoPago)
- Checkout Pro con redirect al sandbox/producción de MercadoPago
- Webhook para notificaciones de pago
- Actualización automática del estado de venta según resultado del pago
- Soporte de tarjeta y billetera MercadoPago

### Dashboard y Reportes
- Resumen de ventas: hoy, semana, mes
- Top 5 productos más vendidos
- Alertas de stock bajo
- Revenue por categoría
- Ventas por canal (online vs interno)
- Reportes con período configurable (7, 30, 90 días)

## Estructura del Proyecto

```
backend/
├── main.py                          # App FastAPI + CORS
├── requirements.txt                 # Dependencias
├── alembic.ini                      # Config de migraciones
├── .env.example                     # Variables de entorno (template)
├── api/
│   ├── deps.py                      # Dependencies (auth, roles)
│   └── api_v1/
│       ├── api.py                   # Router principal
│       └── endpoints/
│           ├── auth.py              # Login, registro
│           ├── users.py             # CRUD usuarios
│           ├── catalog.py           # Categorías, productos, variantes
│           ├── sales.py             # Ventas
│           ├── purchasing.py        # Proveedores, órdenes de compra
│           ├── inventory.py         # Stock, movimientos, ajustes
│           ├── dashboard.py         # Dashboard resumen
│           ├── reports.py           # Reportes de ventas
│           └── payments.py          # MercadoPago integration
├── core/
│   ├── config.py                    # Settings (env vars)
│   └── security.py                  # JWT + password hashing
├── crud/
│   └── user.py                      # CRUD genérico de usuarios
├── db/
│   ├── base.py                      # DeclarativeBase
│   └── session.py                   # Engine + get_db()
├── models/
│   ├── user.py                      # User model
│   ├── catalog.py                   # Category, Product, ProductVariant
│   ├── sales.py                     # Sale, SaleItem
│   ├── purchasing.py                # Supplier, PurchaseOrder, PurchaseOrderItem
│   └── inventory.py                 # InventoryMovement
├── schemas/
│   ├── user.py                      # User schemas
│   ├── catalog.py                   # Catalog schemas
│   ├── sales.py                     # Sales schemas
│   ├── purchasing.py                # Purchasing schemas
│   ├── inventory.py                 # Inventory schemas
│   ├── dashboard.py                 # Dashboard schemas
│   └── reports.py                   # Reports schemas
├── scripts/
│   ├── seed.py                      # Datos demo básicos
│   └── populate_premium.py          # Catálogo premium completo
├── alembic/
│   ├── env.py
│   └── versions/                    # Migraciones
└── templates/                       # Templates (futuro)
```

## Instalación

### Prerequisitos
- Python 3.11+
- PostgreSQL 15+

### 1. Clonar el repositorio
```bash
git clone https://github.com/luca-deganutti/Tienda_ropa_backend.git
cd Tienda_ropa_backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus datos reales
```

### 5. Crear la base de datos
```sql
CREATE DATABASE clothing_store;
```

### 6. Ejecutar migraciones
```bash
alembic upgrade head
```

### 7. (Opcional) Cargar datos de prueba
```bash
# Datos mínimos
python scripts/seed.py

# Catálogo completo con ventas de ejemplo
python scripts/populate_premium.py
```

### 8. Iniciar el servidor
```bash
uvicorn main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`

## Documentación de la API

Una vez iniciado el servidor:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/api/v1/openapi.json

## Endpoints

### Auth (`/api/v1/auth`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/login` | Login con email y password | No |
| POST | `/register` | Registro de cliente | No |

### Users (`/api/v1/users`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/me` | Perfil del usuario actual | Token |
| PUT | `/me` | Actualizar perfil propio | Token |
| GET | `/` | Listar usuarios | Owner |
| POST | `/` | Crear usuario con rol | Owner |
| PUT | `/{user_id}` | Actualizar usuario | Owner |

### Catalog (`/api/v1/catalog`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/categories` | Listar categorías | No |
| POST | `/categories` | Crear categoría | Staff+ |
| PUT | `/categories/{id}` | Actualizar categoría | Staff+ |
| DELETE | `/categories/{id}` | Eliminar categoría | Staff+ |
| GET | `/products` | Listar productos | No |
| GET | `/products/{id}` | Detalle de producto | No |
| POST | `/products` | Crear producto | Staff+ |
| PUT | `/products/{id}` | Actualizar producto | Staff+ |
| DELETE | `/products/{id}` | Soft delete producto | Staff+ |
| POST | `/products/{id}/variants` | Crear variante | Staff+ |
| GET | `/variants/search?sku=` | Buscar por SKU | Staff+ |

### Sales (`/api/v1/sales`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/` | Crear venta | Token |
| GET | `/` | Listar ventas | Staff+ |

### Purchasing (`/api/v1/purchasing`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/suppliers` | Listar proveedores | Staff+ |
| POST | `/suppliers` | Crear proveedor | Staff+ |
| PUT | `/suppliers/{id}` | Actualizar proveedor | Staff+ |
| DELETE | `/suppliers/{id}` | Soft delete proveedor | Staff+ |
| GET | `/orders` | Listar órdenes de compra | Staff+ |
| GET | `/orders/{id}` | Detalle de orden | Staff+ |
| POST | `/orders` | Crear orden de compra | Staff+ |
| POST | `/orders/{id}/receive` | Recibir mercadería | Staff+ |

### Inventory (`/api/v1/inventory`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/stock` | Stock actual | Staff+ |
| GET | `/movements` | Historial de movimientos | Staff+ |
| POST | `/adjust` | Ajuste manual de stock | Staff+ |

### Dashboard (`/api/v1/dashboard`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/` | Resumen general | Staff+ |

### Reports (`/api/v1/reports`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/?days=30` | Reporte de ventas | Staff+ |

### Payments (`/api/v1/payments`)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/public-key` | Public key de MP | No |
| POST | `/create-preference/{sale_id}` | Crear preferencia de pago | Token |
| POST | `/webhook` | Webhook de MercadoPago | No |

## Testing con MercadoPago

Para probar pagos en sandbox:

1. Obtené credenciales de prueba en [MercadoPago Developers](https://www.mercadopago.com.ar/developers)
2. Configuralas en `.env`
3. Usá la tarjeta de prueba:
   - **Número**: `4509 9535 6623 3704`
   - **Vencimiento**: `11/25`
   - **CVV**: `123`
   - **Nombre**: `APRO`
   - **DNI**: `12345678`

## Modelo de Datos

```
User ──────────────────────────────────────────────┐
  │                                                 │
  │ (customer_id)              (seller_id)          │
  ▼                                                 │
Sale ◄──────────────────────────────────────────────┘
  │
  ├── SaleItem ──► ProductVariant ──► Product ──► Category
  │                     │
  │                     ├── InventoryMovement
  │                     │
  │                     └── PurchaseOrderItem ──► PurchaseOrder ──► Supplier
  │
  └── MercadoPago (mp_preference_id, mp_payment_id)
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://postgres:postgres@localhost:5432/clothing_store` |
| `SECRET_KEY` | Clave secreta para JWT | `development_secret_key_change_in_production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token (min) | `11520` (8 días) |
| `MP_ACCESS_TOKEN` | Access token de MercadoPago | `""` |
| `MP_PUBLIC_KEY` | Public key de MercadoPago | `""` |
| `FRONTEND_URL` | URL del frontend | `http://localhost:5173` |

## Autor

**Luca Deganutti** - [GitHub](https://github.com/luca-deganutti)

## Licencia

Este proyecto es privado y de uso comercial.
