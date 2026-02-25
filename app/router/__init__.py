from app.router.auth import router as auth_router
from app.router.categories import router as categories_router
from app.router.catalog import router as catalog_router
from app.router.sales import router as sales_router
from app.router.users import router as users_router

__all__ = ["auth_router", "catalog_router", "categories_router", "users_router", "sales_router"]
