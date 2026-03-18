from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import User, UserRole
from schemas.user import User as UserSchema, UserCreate, UserUpdate
import crud.user as crud_user
from api.deps import get_current_active_user, RoleChecker

router = APIRouter()

allow_owner = RoleChecker([UserRole.owner])

@router.get("/me", response_model=UserSchema)
def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user profile."""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update own user profile."""
    user = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

# --- Admin endpoints (owner only) ---
@router.get("/", response_model=List[UserSchema], dependencies=[Depends(allow_owner)])
def read_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    """List all users (owner only)."""
    return crud_user.user.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=UserSchema, dependencies=[Depends(allow_owner)])
def create_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """Create new user with any role (owner only)."""
    existing = crud_user.user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.user.create(db, obj_in=user_in)

@router.put("/{user_id}", response_model=UserSchema, dependencies=[Depends(allow_owner)])
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """Update any user (owner only)."""
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.user.update(db, db_obj=user, obj_in=user_in)
