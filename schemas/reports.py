from pydantic import BaseModel
from typing import List

class CategoryRevenue(BaseModel):
    category: str
    revenue: float
    units: int

class SalesByChannel(BaseModel):
    online: int
    internal: int

class ReportResponse(BaseModel):
    period: str
    total_revenue: float
    total_sales: int
    avg_order_value: float
    sales_by_channel: SalesByChannel
    revenue_by_category: List[CategoryRevenue]
