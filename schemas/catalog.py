from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class CategoryInDBBase(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class Category(CategoryInDBBase):
    pass

# Product Variant Schemas
class ProductVariantBase(BaseModel):
    sku: str = Field(..., max_length=100)
    color: str = Field(..., max_length=50)
    size: str = Field(..., max_length=20)
    price_override: Optional[float] = None
    min_stock: int = 5
    is_active: bool = True

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantUpdate(ProductVariantBase):
    sku: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None

class ProductVariantInDBBase(ProductVariantBase):
    id: int
    product_id: int
    created_at: datetime
    price: float # Computed property from model

    class Config:
        from_attributes = True

class ProductVariant(ProductVariantInDBBase):
    pass

# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    base_price: float = Field(..., gt=0)
    category_id: int
    is_active: bool = True
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    base_price: Optional[float] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None

class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Product(ProductInDBBase):
    variants: List[ProductVariant] = []
    category: Optional[Category] = None
