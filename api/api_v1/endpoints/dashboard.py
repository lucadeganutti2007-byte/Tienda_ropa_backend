from typing import Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from db.database import get_db
from models.sales import Sale, SaleItem, SaleStatus
from models.catalog import Product, ProductVariant
from models.inventory import InventoryMovement 
from models.purchasing import PurchaseOrder, OrderStatus
from models.user import User, UserRole
from schemas.dashboard import (
    DashboardResponse,
    SalesPeriodSummary,
    TopProductItem,
)
from api.deps import RoleChecker

router = APIRouter()

allow_admin_staff = RoleChecker([UserRole.owner, UserRole.admin, UserRole.staff])


def _get_sales_summary(db: Session, since: datetime, period_label: str) -> SalesPeriodSummary:
    """Helper: count sales and sum revenue since a given datetime."""
    result = (
        db.query(
            func.count(Sale.id).label("cnt"),
            func.coalesce(func.sum(Sale.total_amount), 0).label("rev"),
        )
        .filter(
            Sale.created_at >= since,
            Sale.status != SaleStatus.cancelled,
        )
        .one()
    )
    return SalesPeriodSummary(
        period=period_label,
        total_sales_count=result.cnt,
        total_revenue=float(result.rev),
    )


def _get_top_products(db: Session, limit: int = 5):
    """Helper: top N products by quantity sold (all time)."""
    rows = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.coalesce(func.sum(SaleItem.quantity), 0).label("total_qty"),
            func.coalesce(func.sum(SaleItem.quantity * SaleItem.unit_price), 0).label("total_rev"),
        )
        .join(ProductVariant, ProductVariant.product_id == Product.id)
        .join(SaleItem, SaleItem.variant_id == ProductVariant.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.status != SaleStatus.cancelled)
        .group_by(Product.id, Product.name)
        .order_by(desc("total_qty"))
        .limit(limit)
        .all()
    )
    return [
        TopProductItem(
            product_id=r.product_id,
            product_name=r.product_name,
            total_quantity_sold=int(r.total_qty),
            total_revenue=float(r.total_rev),
        )
        for r in rows
    ]


def _count_low_stock(db: Session) -> int:
    """Count variants whose current stock <= min_stock."""
    variants = (
        db.query(ProductVariant)
        .filter(ProductVariant.is_active == True)
        .all()
    )
    count = 0
    for v in variants:
        total = (
            db.query(func.coalesce(func.sum(InventoryMovement.quantity), 0))
            .filter(InventoryMovement.variant_id == v.id)
            .scalar()
        )
        if total <= v.min_stock:
            count += 1
    return count


@router.get("/", response_model=DashboardResponse, dependencies=[Depends(allow_admin_staff)])
def get_dashboard(db: Session = Depends(get_db)) -> Any:
    """
    Returns the admin dashboard summary:
    - Sales today / this week / this month
    - Top 5 products by quantity sold
    - Low stock alerts count
    - Pending purchase orders count
    - Total active products, variants, and customers
    """
    now = datetime.utcnow()

    # Period boundaries
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday
    month_start = today_start.replace(day=1)

    # Sales summaries
    sales_today = _get_sales_summary(db, today_start, "today")
    sales_week = _get_sales_summary(db, week_start, "week")
    sales_month = _get_sales_summary(db, month_start, "month")

    # Top products
    top_products = _get_top_products(db, limit=5)

    # Low stock
    low_stock_count = _count_low_stock(db)

    # Pending purchase orders
    pending_po = (
        db.query(func.count(PurchaseOrder.id))
        .filter(PurchaseOrder.status.in_([OrderStatus.draft, OrderStatus.sent, OrderStatus.partially_received]))
        .scalar()
    )

    # Totals
    total_active_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_active_variants = db.query(func.count(ProductVariant.id)).filter(ProductVariant.is_active == True).scalar()
    total_customers = db.query(func.count(User.id)).filter(User.role == UserRole.customer).scalar()

    return DashboardResponse(
        sales_today=sales_today,
        sales_week=sales_week,
        sales_month=sales_month,
        top_products=top_products,
        low_stock_alerts_count=low_stock_count,
        pending_purchase_orders_count=pending_po,
        total_active_products=total_active_products,
        total_active_variants=total_active_variants,
        total_customers=total_customers,
    )
