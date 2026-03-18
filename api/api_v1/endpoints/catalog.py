from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.catalog import Category, Product, ProductVariant
from models.user import UserRole
from schemas.catalog import (
    Category as CategorySchema, CategoryCreate, CategoryUpdate,
    Product as ProductSchema, ProductCreate, ProductUpdate,
    ProductVariant as VariantSchema, ProductVariantCreate, ProductVariantUpdate
)
from api.deps import get_current_active_user, RoleChecker

router = APIRouter()

allow_admin_staff = RoleChecker([UserRole.owner, UserRole.admin, UserRole.staff])

# --- Categories ---
@router.get("/categories", response_model=List[CategorySchema])
def read_categories(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    return db.query(Category).offset(skip).limit(limit).all()

@router.post("/categories", response_model=CategorySchema, dependencies=[Depends(allow_admin_staff)])
def create_category(*, db: Session = Depends(get_db), category_in: CategoryCreate) -> Any:
    category = db.query(Category).filter(Category.name == category_in.name).first()
    if category:
        raise HTTPException(status_code=400, detail="Category already exists.")
    category = Category(**category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.put("/categories/{id}", response_model=CategorySchema, dependencies=[Depends(allow_admin_staff)])
def update_category(*, db: Session = Depends(get_db), id: int, category_in: CategoryUpdate) -> Any:
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{id}", dependencies=[Depends(allow_admin_staff)])
def delete_category(*, db: Session = Depends(get_db), id: int) -> Any:
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    active_products_count = db.query(Product).filter(
        Product.category_id == id, Product.is_active == True
    ).count()
    if active_products_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {active_products_count} active product(s). Deactivate them first."
        )
    category_id = category.id
    category_name = category.name
    db.delete(category)
    db.commit()
    return {"id": category_id, "name": category_name, "message": "Category deleted successfully"}

# --- Products ---
@router.get("/products", response_model=List[ProductSchema])
def read_products(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, active_only: bool = True) -> Any:
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.offset(skip).limit(limit).all()

@router.get("/products/{id}", response_model=ProductSchema)
def read_product(id: int, db: Session = Depends(get_db)) -> Any:
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=ProductSchema, dependencies=[Depends(allow_admin_staff)])
def create_product(*, db: Session = Depends(get_db), product_in: ProductCreate) -> Any:
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/products/{id}", response_model=ProductSchema, dependencies=[Depends(allow_admin_staff)])
def update_product(*, db: Session = Depends(get_db), id: int, product_in: ProductUpdate) -> Any:
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{id}", response_model=ProductSchema, dependencies=[Depends(allow_admin_staff)])
def delete_product(*, db: Session = Depends(get_db), id: int) -> Any:
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product

# --- Variants ---
@router.post("/products/{product_id}/variants", response_model=VariantSchema, dependencies=[Depends(allow_admin_staff)])
def create_variant(
    *, 
    db: Session = Depends(get_db), 
    product_id: int, 
    variant_in: ProductVariantCreate
) -> Any:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_var = db.query(ProductVariant).filter(ProductVariant.sku == variant_in.sku).first()
    if existing_var:
        raise HTTPException(status_code=400, detail="Variant with this SKU already exists")
        
    variant = ProductVariant(**variant_in.model_dump(), product_id=product_id)
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant

@router.get("/variants/search", response_model=List[VariantSchema], dependencies=[Depends(allow_admin_staff)])
def search_variants(sku: str, db: Session = Depends(get_db)) -> Any:
    return db.query(ProductVariant).filter(ProductVariant.sku.ilike(f"%{sku}%")).all()
