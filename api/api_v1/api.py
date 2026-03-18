from fastapi import APIRouter
from api.api_v1.endpoints import auth, catalog, sales, users, purchasing, inventory, dashboard, reports, payments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(purchasing.router, prefix="/purchasing", tags=["purchasing"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])


