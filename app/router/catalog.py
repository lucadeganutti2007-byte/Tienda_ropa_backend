from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_admin
from app.crud import catalog as catalog_crud
from app.schemas.catalog import (
    ProductCreate,
    ProductImageCreate,
    ProductImageRead,
    ProductImageUpdate,
    ProductRead,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
)

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/products", response_model=list[ProductRead])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    only_active: bool = True,
    db: Session = Depends(get_db),
):
    return catalog_crud.list_products(db, skip=skip, limit=limit, only_active=only_active)


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = catalog_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = catalog_crud.create_product(
        db,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category_id=payload.category_id,
        is_active=payload.is_active,
    )
    return catalog_crud.get_product(db, product.id)


@router.put("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_admin)])
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = catalog_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    updated = catalog_crud.update_product(
        db,
        product,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category_id=payload.category_id,
        is_active=payload.is_active,
    )
    return catalog_crud.get_product(db, updated.id)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = catalog_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    catalog_crud.delete_product(db, product)


@router.get("/products/{product_id}/variants", response_model=list[ProductVariantRead])
def list_product_variants(product_id: int, db: Session = Depends(get_db)):
    return catalog_crud.list_variants_by_product(db, product_id)


@router.post(
    "/products/{product_id}/variants",
    response_model=ProductVariantRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_variant(product_id: int, payload: ProductVariantCreate, db: Session = Depends(get_db)):
    try:
        return catalog_crud.create_variant(
            db,
            product_id=product_id,
            sku=payload.sku,
            size=payload.size,
            color=payload.color,
            stock=payload.stock,
            price_override=payload.price_override,
            is_active=payload.is_active,
            images=[(img.image_url, img.position) for img in payload.images],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/variants/{variant_id}", response_model=ProductVariantRead)
def get_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = catalog_crud.get_variant(db, variant_id)
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")
    return variant


@router.put("/variants/{variant_id}", response_model=ProductVariantRead, dependencies=[Depends(require_admin)])
def update_variant(variant_id: int, payload: ProductVariantUpdate, db: Session = Depends(get_db)):
    variant = catalog_crud.get_variant(db, variant_id)
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")
    try:
        return catalog_crud.update_variant(
            db,
            variant,
            sku=payload.sku,
            size=payload.size,
            color=payload.color,
            stock=payload.stock,
            price_override=payload.price_override,
            is_active=payload.is_active,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = catalog_crud.get_variant(db, variant_id)
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")
    catalog_crud.delete_variant(db, variant)


@router.post(
    "/variants/{variant_id}/images",
    response_model=ProductImageRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_variant_image(variant_id: int, payload: ProductImageCreate, db: Session = Depends(get_db)):
    try:
        return catalog_crud.create_variant_image(
            db,
            variant_id=variant_id,
            image_url=payload.image_url,
            position=payload.position,
        )
    except ValueError as exc:
        message = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc


@router.put("/images/{image_id}", response_model=ProductImageRead, dependencies=[Depends(require_admin)])
def update_image(image_id: int, payload: ProductImageUpdate, db: Session = Depends(get_db)):
    image = catalog_crud.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    try:
        return catalog_crud.update_variant_image(
            db,
            image,
            image_url=payload.image_url,
            position=payload.position,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = catalog_crud.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    catalog_crud.delete_variant_image(db, image)
