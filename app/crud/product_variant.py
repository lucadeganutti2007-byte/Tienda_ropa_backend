from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import catalog
from app.models.productVariant import ProductVariant


def list_variants_by_product(db: Session, product_id: int) -> Sequence[ProductVariant]:
    return catalog.list_variants_by_product(db, product_id)


def get_variant(db: Session, variant_id: int) -> ProductVariant | None:
    return catalog.get_variant(db, variant_id)


def create_variant(
    db: Session,
    *,
    product_id: int,
    sku: str,
    size: str,
    color: str,
    stock: int = 0,
    price_override: Decimal | None = None,
    is_active: bool = True,
    images: list[tuple[str, int]] | None = None,
) -> ProductVariant:
    return catalog.create_variant(
        db,
        product_id=product_id,
        sku=sku,
        size=size,
        color=color,
        stock=stock,
        price_override=price_override,
        is_active=is_active,
        images=images,
    )


def update_variant(
    db: Session,
    variant: ProductVariant,
    *,
    sku: str | None = None,
    size: str | None = None,
    color: str | None = None,
    stock: int | None = None,
    price_override: Decimal | None = None,
    is_active: bool | None = None,
) -> ProductVariant:
    return catalog.update_variant(
        db,
        variant,
        sku=sku,
        size=size,
        color=color,
        stock=stock,
        price_override=price_override,
        is_active=is_active,
    )


def delete_variant(db: Session, variant: ProductVariant) -> None:
    catalog.delete_variant(db, variant)
