from sqlalchemy.orm import Session

from app.models.Category import Category


def list_categories(db: Session, skip: int = 0, limit: int = 50, only_active: bool = True) -> list[Category]:
    query = db.query(Category).offset(skip).limit(limit)
    if only_active:
        query = query.filter(Category.is_active.is_(True))
    return query.all()


def get_category(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return db.query(Category).filter(Category.slug == slug).first()


def create_category(db: Session, *, name: str, slug: str, is_active: bool = True) -> Category:
    category = Category(name=name, slug=slug, is_active=is_active)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session,
    category: Category,
    *,
    name: str | None = None,
    slug: str | None = None,
    is_active: bool | None = None,
) -> Category:
    if name is not None:
        category.name = name
    if slug is not None:
        category.slug = slug
    if is_active is not None:
        category.is_active = is_active
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
