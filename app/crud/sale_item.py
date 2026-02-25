from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.Products import Product
from app.models.Sale import Sale
from app.models.SaleItem import SaleItem


def list_sale_items(db: Session, sale_id: int) -> list[SaleItem]:
    return db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()


def get_sale_item(db: Session, sale_item_id: int) -> SaleItem | None:
    return db.query(SaleItem).filter(SaleItem.id == sale_item_id).first()


def _recalculate_total(db: Session, sale_id: int) -> None:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return
    items = db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
    total = Decimal("0.00")
    for item in items:
        total += Decimal(str(item.unit_price)) * item.quantity
    sale.total_amount = total


def create_sale_item(
    db: Session,
    *,
    sale_id: int,
    product_id: int,
    quantity: int,
    unit_price: Decimal | None = None,
) -> SaleItem:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise ValueError("Sale not found.")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("Product not found.")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0.")

    final_price = unit_price if unit_price is not None else Decimal(str(product.price))
    if final_price <= 0:
        raise ValueError("Unit price must be greater than 0.")

    sale_item = SaleItem(
        sale_id=sale_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=final_price,
    )
    db.add(sale_item)
    db.flush()
    _recalculate_total(db, sale_id)
    db.commit()
    db.refresh(sale_item)
    return sale_item


def update_sale_item(
    db: Session,
    sale_item: SaleItem,
    *,
    product_id: int | None = None,
    quantity: int | None = None,
    unit_price: Decimal | None = None,
) -> SaleItem:
    if product_id is not None:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found.")
        sale_item.product_id = product_id

    if quantity is not None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        sale_item.quantity = quantity

    if unit_price is not None:
        if unit_price <= 0:
            raise ValueError("Unit price must be greater than 0.")
        sale_item.unit_price = unit_price

    _recalculate_total(db, sale_item.sale_id)
    db.commit()
    db.refresh(sale_item)
    return sale_item


def delete_sale_item(db: Session, sale_item: SaleItem) -> None:
    sale_id = sale_item.sale_id
    db.delete(sale_item)
    db.flush()
    _recalculate_total(db, sale_id)
    db.commit()
