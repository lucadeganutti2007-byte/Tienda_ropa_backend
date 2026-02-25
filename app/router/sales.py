from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, require_admin
from app.crud import sale as sale_crud
from app.schemas.sale import SaleCreate, SaleRead

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return sale_crud.create_sale(
            db,
            user_id=current_user.id,
            items=[(item.product_id, item.quantity, item.unit_price) for item in payload.items],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/me", response_model=list[SaleRead])
def list_my_sales(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sale_crud.list_sales_by_user(db, current_user.id, skip=skip, limit=limit)


@router.get("", response_model=list[SaleRead], dependencies=[Depends(require_admin)])
def list_all_sales(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return sale_crud.list_sales(db, skip=skip, limit=limit)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    sale = sale_crud.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found.")

    if current_user.role != "admin" and sale.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions.")
    return sale


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = sale_crud.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found.")
    sale_crud.delete_sale(db, sale)
