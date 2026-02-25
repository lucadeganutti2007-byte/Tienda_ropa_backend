from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_admin
from app.crud import category as category_crud
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    only_active: bool = True,
    db: Session = Depends(get_db),
):
    return category_crud.list_categories(db, skip=skip, limit=limit, only_active=only_active)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = category_crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return category


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    if category_crud.get_category_by_slug(db, payload.slug):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists.")
    return category_crud.create_category(db, name=payload.name, slug=payload.slug, is_active=payload.is_active)


@router.put("/{category_id}", response_model=CategoryRead, dependencies=[Depends(require_admin)])
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = category_crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    if payload.slug:
        existing = category_crud.get_category_by_slug(db, payload.slug)
        if existing and existing.id != category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists.")
    return category_crud.update_category(
        db,
        category,
        name=payload.name,
        slug=payload.slug,
        is_active=payload.is_active,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = category_crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    category_crud.delete_category(db, category)
