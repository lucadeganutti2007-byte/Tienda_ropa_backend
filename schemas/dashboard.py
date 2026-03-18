from pydantic import BaseModel
from typing import List


class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_revenue: float


class SalesPeriodSummary(BaseModel):
    period: str  # "today", "week", "month"
    total_sales_count: int
    total_revenue: float


class DashboardResponse(BaseModel):
    sales_today: SalesPeriodSummary
    sales_week: SalesPeriodSummary
    sales_month: SalesPeriodSummary
    top_products: List[TopProductItem]
    low_stock_alerts_count: int
    pending_purchase_orders_count: int
    total_active_products: int
    total_active_variants: int
    total_customers: int
