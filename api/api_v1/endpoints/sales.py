from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from models.sales import Sale, SaleItem as SaleItemModel, SaleStatus, SaleType
from models.inventory import InventoryMovement, MovementType
from models.catalog import ProductVariant
from models.user import User, UserRole
from schemas.sales import Sale as SaleSchema, SaleCreate
from api.deps import get_current_active_user, RoleChecker

router = APIRouter()

allow_staff = RoleChecker([UserRole.owner, UserRole.admin, UserRole.staff])


def _get_available_stock(db: Session, variant_id: int) -> int:
    """Calculate current available stock for a variant by summing all inventory movements."""
    total = (
        db.query(func.coalesce(func.sum(InventoryMovement.quantity), 0))
        .filter(InventoryMovement.variant_id == variant_id)
        .scalar()
    )
    return int(total)


@router.post("/", response_model=SaleSchema)
def create_sale(
    *,
    db: Session = Depends(get_db),
    sale_in: SaleCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    # 1. Validate variants exist, are active, have enough stock, and calculate total
    total_amount = 0.0
    stock_errors = []

    for item in sale_in.items:
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail=f"Variant {item.variant_id} not found")

        if not variant.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Variant {variant.sku} is not active and cannot be sold",
            )

        available = _get_available_stock(db, variant.id)
        if available < item.quantity:
            stock_errors.append(
                {
                    "variant_id": variant.id,
                    "sku": variant.sku,
                    "requested": item.quantity,
                    "available": available,
                }
            )

        total_amount += item.quantity * item.unit_price

    # If any variant has insufficient stock, reject the entire sale
    if stock_errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Insufficient stock for one or more variants",
                "items": stock_errors,
            },
        )

    # 2. Create Sale
    db_sale = Sale(
        sale_type=sale_in.sale_type,
        status=SaleStatus.pending,
        total_amount=total_amount,
        shipping_address=sale_in.shipping_address,
        customer_id=current_user.id if current_user.role == UserRole.customer else None,
        seller_id=current_user.id if current_user.role != UserRole.customer else None,
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    # 3. Create items and Inventory Movements (stock deduction)
    for item in sale_in.items:
        db_item = SaleItemModel(
            sale_id=db_sale.id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        db.add(db_item)

        movement_type = (
            MovementType.out_sale_online
            if sale_in.sale_type == SaleType.online
            else MovementType.out_sale_internal
        )
        db_movement = InventoryMovement(
            variant_id=item.variant_id,
            quantity=-item.quantity,  # Negative for outgoing
            movement_type=movement_type,
            reference_id=db_sale.id,
            notes=f"Sale #{db_sale.id}",
        )
        db.add(db_movement)

    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=List[SaleSchema], dependencies=[Depends(allow_staff)])
def list_sales(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    return db.query(Sale).order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()

