from collections.abc import Sequence
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.models.Products import Product
from app.models.Sale import Sale
from app.models.SaleItem import SaleItem


def list_sales(db: Session, skip: int = 0, limit: int = 50) -> Sequence[Sale]:
    return (
        db.query(Sale)
        .options(selectinload(Sale.items))
        .order_by(Sale.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_sales_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> Sequence[Sale]:
    return (
        db.query(Sale)
        .options(selectinload(Sale.items))
        .filter(Sale.user_id == user_id)
        .order_by(Sale.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_sale(db: Session, sale_id: int) -> Sale | None:
    return db.query(Sale).options(selectinload(Sale.items)).filter(Sale.id == sale_id).first()


def _build_sale_items_and_total(
    db: Session, items: list[tuple[int, int, Decimal | None]]
) -> tuple[list[SaleItem], Decimal]:
    if not items:
        raise ValueError("A sale must include at least one item.")

    sale_items: list[SaleItem] = []
    total_amount = Decimal("0.00")
    for product_id, quantity, unit_price in items:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product {product_id} not found.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        applied_price = unit_price if unit_price is not None else Decimal(str(product.price))
        if applied_price <= 0:
            raise ValueError("Unit price must be greater than 0.")
        total_amount += applied_price * quantity
        sale_items.append(
            SaleItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=applied_price,
            )
        )
    return sale_items, total_amount


def create_sale(
    db: Session,
    *,
    user_id: int,
    items: list[tuple[int, int, Decimal | None]],
) -> Sale:
    sale_items, total_amount = _build_sale_items_and_total(db, items)

    sale = Sale(
        date=datetime.now(timezone.utc),
        total_amount=total_amount,
        user_id=user_id,
        items=sale_items,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return get_sale(db, sale.id)  # type: ignore[return-value]


def update_sale(
    db: Session,
    sale: Sale,
    *,
    items: list[tuple[int, int, Decimal | None]],
) -> Sale:
    sale_items, total_amount = _build_sale_items_and_total(db, items)

    sale.items.clear()
    for item in sale_items:
        sale.items.append(item)
    sale.total_amount = total_amount

    db.commit()
    db.refresh(sale)
    return get_sale(db, sale.id)  # type: ignore[return-value]


def delete_sale(db: Session, sale: Sale) -> None:
    db.delete(sale)
    db.commit()
