from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import catalog
from app.models.Products import Product


def list_products(db: Session, skip: int = 0, limit: int = 50, only_active: bool = True) -> Sequence[Product]:
    return catalog.list_products(db, skip=skip, limit=limit, only_active=only_active)


def get_product(db: Session, product_id: int) -> Product | None:
    return catalog.get_product(db, product_id)


def create_product(
    db: Session,
    *,
    name: str,
    description: str | None,
    price: Decimal,
    category_id: int,
    is_active: bool = True,
) -> Product:
    return catalog.create_product(
        db,
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        is_active=is_active,
    )


def update_product(
    db: Session,
    product: Product,
    *,
    name: str | None = None,
    description: str | None = None,
    price: Decimal | None = None,
    category_id: int | None = None,
    is_active: bool | None = None,
) -> Product:
    return catalog.update_product(
        db,
        product,
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        is_active=is_active,
    )


def delete_product(db: Session, product: Product) -> None:
    catalog.delete_product(db, product)
