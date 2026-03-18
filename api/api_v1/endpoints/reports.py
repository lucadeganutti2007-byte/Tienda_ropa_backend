from typing import Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from models.sales import Sale, SaleItem as SaleItemModel, SaleType
from models.catalog import Product, Category, ProductVariant
from models.user import UserRole
from schemas.reports import ReportResponse, CategoryRevenue, SalesByChannel
from api.deps import RoleChecker

router = APIRouter()
allow_admin_staff = RoleChecker([UserRole.owner, UserRole.admin, UserRole.staff])

@router.get("/", response_model=ReportResponse, dependencies=[Depends(allow_admin_staff)])
def get_reports(db: Session = Depends(get_db), days: int = 30) -> Any:
    since = datetime.utcnow() - timedelta(days=days)
    sales = db.query(Sale).filter(Sale.created_at >= since).all()

    total_revenue = sum(s.total_amount for s in sales)
    total_sales = len(sales)
    avg_order_value = total_revenue / total_sales if total_sales > 0 else 0

    online_count = sum(1 for s in sales if s.sale_type == SaleType.online)
    internal_count = total_sales - online_count

    # Revenue by category
    category_data: dict = {}
    for sale in sales:
        items = db.query(SaleItemModel).filter(SaleItemModel.sale_id == sale.id).all()
        for item in items:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
            if not variant:
                continue
            product = db.query(Product).filter(Product.id == variant.product_id).first()
            if not product:
                continue
            category = db.query(Category).filter(Category.id == product.category_id).first()
            cat_name = category.name if category else "Sin categoría"
            if cat_name not in category_data:
                category_data[cat_name] = {"revenue": 0.0, "units": 0}
            category_data[cat_name]["revenue"] += item.quantity * item.unit_price
            category_data[cat_name]["units"] += item.quantity

    revenue_by_category = [
        CategoryRevenue(category=k, revenue=v["revenue"], units=v["units"])
        for k, v in category_data.items()
    ]

    return ReportResponse(
        period=f"last_{days}_days",
        total_revenue=total_revenue,
        total_sales=total_sales,
        avg_order_value=avg_order_value,
        sales_by_channel=SalesByChannel(online=online_count, internal=internal_count),
        revenue_by_category=revenue_by_category,
    )
