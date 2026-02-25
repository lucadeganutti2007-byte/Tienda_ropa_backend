from fastapi import FastAPI

from app.core.db import Base, engine
from app.models import Category, Product, ProductImage, ProductVariant, Sale, SaleItem, User  # noqa: F401
from app.router.auth import router as auth_router
from app.router.catalog import router as catalog_router
from app.router.categories import router as categories_router
from app.router.sales import router as sales_router
from app.router.users import router as users_router

app = FastAPI(title="Tienda de Ropa API")

app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(categories_router)
app.include_router(users_router)
app.include_router(sales_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
