from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from models.inventory import InventoryMovement, MovementType
from models.catalog import ProductVariant, Product
from models.user import UserRole
from schemas.inventory import (
    InventoryMovement as MovementSchema,
    InventoryMovementCreate,
    StockLevel,
)
from api.deps import RoleChecker

router = APIRouter()

allow_admin_staff = RoleChecker([UserRole.owner, UserRole.admin, UserRole.staff])

@router.get("/stock", response_model=List[StockLevel], dependencies=[Depends(allow_admin_staff)])
def get_stock_levels(db: Session = Depends(get_db), low_only: bool = False) -> Any:
    """Get current stock levels for all variants."""
    variants = db.query(ProductVariant).filter(ProductVariant.is_active == True).all()
    result = []
    for v in variants:
        total = db.query(func.coalesce(func.sum(InventoryMovement.quantity), 0)).filter(
            InventoryMovement.variant_id == v.id
        ).scalar()
        product = db.query(Product).filter(Product.id == v.product_id).first()
        is_low = total <= v.min_stock
        if low_only and not is_low:
            continue
        result.append(StockLevel(
            variant_id=v.id,
            sku=v.sku,
            product_name=product.name if product else "Unknown",
            color=v.color,
            size=v.size,
            current_stock=total,
            min_stock=v.min_stock,
            is_low=is_low,
        ))
    return result

@router.get("/movements", response_model=List[MovementSchema], dependencies=[Depends(allow_admin_staff)])
def list_movements(
    db: Session = Depends(get_db),
    variant_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List inventory movements, optionally filtered by variant."""
    query = db.query(InventoryMovement)
    if variant_id:
        query = query.filter(InventoryMovement.variant_id == variant_id)
    return query.order_by(InventoryMovement.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/adjust", response_model=MovementSchema, dependencies=[Depends(allow_admin_staff)])
def create_adjustment(*, db: Session = Depends(get_db), movement_in: InventoryMovementCreate) -> Any:
    """Create a manual inventory adjustment."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == movement_in.variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    movement = InventoryMovement(
        variant_id=movement_in.variant_id,
        quantity=movement_in.quantity,
        movement_type=MovementType.adjustment,
        notes=movement_in.notes,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
