from sqlalchemy.orm import Session

from app.crud import catalog
from app.models.productImage import ProductImage


def get_image(db: Session, image_id: int) -> ProductImage | None:
    return catalog.get_image(db, image_id)


def create_variant_image(
    db: Session,
    *,
    variant_id: int,
    image_url: str,
    position: int,
) -> ProductImage:
    return catalog.create_variant_image(
        db,
        variant_id=variant_id,
        image_url=image_url,
        position=position,
    )


def update_variant_image(
    db: Session,
    image: ProductImage,
    *,
    image_url: str | None = None,
    position: int | None = None,
) -> ProductImage:
    return catalog.update_variant_image(db, image, image_url=image_url, position=position)


def delete_variant_image(db: Session, image: ProductImage) -> None:
    catalog.delete_variant_image(db, image)
