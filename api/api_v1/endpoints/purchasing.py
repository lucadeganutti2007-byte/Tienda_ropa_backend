from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.purchasing import Supplier, PurchaseOrder, PurchaseOrderItem as POItemModel, OrderStatus
from models.inventory import InventoryMovement, MovementType
from models.user import User, UserRole
from schemas.purchasing import (
    Supplier as SupplierSchema, SupplierCreate, SupplierUpdate,
    PurchaseOrder as POSchema, PurchaseOrderCreate, PurchaseOrderReceive
)
from api.deps import RoleChecker

router = APIRouter()

allow_admin_staff = RoleChecker([UserRole.owner, UserRole.admin, UserRole.staff])

# ==================== SUPPLIERS ====================

@router.get("/suppliers", response_model=List[SupplierSchema], dependencies=[Depends(allow_admin_staff)])
def list_suppliers(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    return db.query(Supplier).offset(skip).limit(limit).all()

@router.post("/suppliers", response_model=SupplierSchema, dependencies=[Depends(allow_admin_staff)])
def create_supplier(*, db: Session = Depends(get_db), supplier_in: SupplierCreate) -> Any:
    supplier = Supplier(**supplier_in.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier

@router.put("/suppliers/{supplier_id}", response_model=SupplierSchema, dependencies=[Depends(allow_admin_staff)])
def update_supplier(*, db: Session = Depends(get_db), supplier_id: int, supplier_in: SupplierUpdate) -> Any:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    update_data = supplier_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier

@router.delete("/suppliers/{supplier_id}", response_model=SupplierSchema, dependencies=[Depends(allow_admin_staff)])
def delete_supplier(*, db: Session = Depends(get_db), supplier_id: int) -> Any:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier.is_active = False
    db.commit()
    db.refresh(supplier)
    return supplier

# ==================== PURCHASE ORDERS ====================

@router.get("/orders", response_model=List[POSchema], dependencies=[Depends(allow_admin_staff)])
def list_purchase_orders(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    return db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/orders/{order_id}", response_model=POSchema, dependencies=[Depends(allow_admin_staff)])
def get_purchase_order(order_id: int, db: Session = Depends(get_db)) -> Any:
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return order

@router.post("/orders", response_model=POSchema, dependencies=[Depends(allow_admin_staff)])
def create_purchase_order(*, db: Session = Depends(get_db), order_in: PurchaseOrderCreate) -> Any:
    # Calculate total
    total = sum(item.quantity * item.unit_cost for item in order_in.items)
    
    db_order = PurchaseOrder(
        supplier_id=order_in.supplier_id,
        status=OrderStatus.draft,
        total_amount=total,
        notes=order_in.notes,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order_in.items:
        db_item = POItemModel(
            order_id=db_order.id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            received_quantity=0,
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/orders/{order_id}/receive", response_model=POSchema, dependencies=[Depends(allow_admin_staff)])
def receive_purchase_order(
    *, db: Session = Depends(get_db), order_id: int, receive_in: PurchaseOrderReceive
) -> Any:
    """
    Mark items as received and create inventory movements (stock in).
    Expects: { "items": [{"item_id": 1, "received_quantity": 10}] }
    """
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot receive a cancelled order")

    all_items_received = True
    for receive_item in receive_in.items:
        po_item = db.query(POItemModel).filter(POItemModel.id == receive_item["item_id"]).first()
        if not po_item or po_item.order_id != order.id:
            raise HTTPException(status_code=404, detail=f"PO Item {receive_item['item_id']} not found in this order")

        qty = receive_item["received_quantity"]
        po_item.received_quantity += qty

        # Create positive inventory movement
        movement = InventoryMovement(
            variant_id=po_item.variant_id,
            quantity=qty,
            movement_type=MovementType.in_purchase,
            reference_id=order.id,
            notes=f"Purchase Order #{order.id} received"
        )
        db.add(movement)

        if po_item.received_quantity < po_item.quantity:
            all_items_received = False

    order.status = OrderStatus.received if all_items_received else OrderStatus.partially_received
    db.commit()
    db.refresh(order)
    return order
