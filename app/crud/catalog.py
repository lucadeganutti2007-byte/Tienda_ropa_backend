from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.models.productImage import ProductImage
from app.models.Products import Product
from app.models.productVariant import ProductVariant


def list_products(db: Session, skip: int = 0, limit: int = 50, only_active: bool = True) -> Sequence[Product]:
    query = (
        db.query(Product)
        .options(
            selectinload(Product.variants).selectinload(ProductVariant.images),
        )
        .offset(skip)
        .limit(limit)
    )
    if only_active:
        query = query.filter(Product.is_active.is_(True))
    return query.all()


def get_product(db: Session, product_id: int) -> Product | None:
    return (
        db.query(Product)
        .options(
            selectinload(Product.variants).selectinload(ProductVariant.images),
        )
        .filter(Product.id == product_id)
        .first()
    )


def create_product(
    db: Session,
    *,
    name: str,
    description: str | None,
    price: Decimal,
    category_id: int,
    is_active: bool = True,
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        is_active=is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session,
    product: Product,
    *,
    name: str | None = None,
    description: str | None = None,
    price: Decimal | None = None,
    category_id: int | None = None,
    is_active: bool | None = None,
) -> Product:
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if category_id is not None:
        product.category_id = category_id
    if is_active is not None:
        product.is_active = is_active

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def list_variants_by_product(db: Session, product_id: int) -> Sequence[ProductVariant]:
    return (
        db.query(ProductVariant)
        .options(selectinload(ProductVariant.images))
        .filter(ProductVariant.product_id == product_id)
        .all()
    )


def get_variant(db: Session, variant_id: int) -> ProductVariant | None:
    return (
        db.query(ProductVariant)
        .options(selectinload(ProductVariant.images))
        .filter(ProductVariant.id == variant_id)
        .first()
    )


def _validate_variant_images(positions: list[int]) -> None:
    if len(positions) > 8:
        raise ValueError("Each variant supports at most 8 images.")
    if len(set(positions)) != len(positions):
        raise ValueError("Image positions must be unique per variant.")


def create_variant(
    db: Session,
    *,
    product_id: int,
    sku: str,
    size: str,
    color: str,
    stock: int = 0,
    price_override: Decimal | None = None,
    is_active: bool = True,
    images: list[tuple[str, int]] | None = None,
) -> ProductVariant:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("Product not found.")

    existing_sku = db.query(ProductVariant).filter(ProductVariant.sku == sku).first()
    if existing_sku:
        raise ValueError("SKU already exists.")

    images = images or []
    positions = [position for _, position in images]
    _validate_variant_images(positions)

    variant = ProductVariant(
        product_id=product_id,
        sku=sku,
        size=size,
        color=color,
        stock=stock,
        price_override=price_override,
        is_active=is_active,
    )
    db.add(variant)
    db.flush()

    for image_url, position in images:
        db.add(
            ProductImage(
                product_variant_id=variant.id,
                image_url=image_url,
                position=position,
            )
        )

    db.commit()
    db.refresh(variant)
    return get_variant(db, variant.id)  # type: ignore[return-value]


def update_variant(
    db: Session,
    variant: ProductVariant,
    *,
    sku: str | None = None,
    size: str | None = None,
    color: str | None = None,
    stock: int | None = None,
    price_override: Decimal | None = None,
    is_active: bool | None = None,
) -> ProductVariant:
    if sku is not None and sku != variant.sku:
        existing_sku = (
            db.query(ProductVariant)
            .filter(ProductVariant.sku == sku, ProductVariant.id != variant.id)
            .first()
        )
        if existing_sku:
            raise ValueError("SKU already exists.")
        variant.sku = sku
    if size is not None:
        variant.size = size
    if color is not None:
        variant.color = color
    if stock is not None:
        variant.stock = stock
    if price_override is not None:
        variant.price_override = price_override
    if is_active is not None:
        variant.is_active = is_active

    db.commit()
    db.refresh(variant)
    return get_variant(db, variant.id)  # type: ignore[return-value]


def delete_variant(db: Session, variant: ProductVariant) -> None:
    db.delete(variant)
    db.commit()


def create_variant_image(
    db: Session,
    *,
    variant_id: int,
    image_url: str,
    position: int,
) -> ProductImage:
    if position < 1 or position > 8:
        raise ValueError("Position must be between 1 and 8.")

    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise ValueError("Variant not found.")

    current_count = db.query(ProductImage).filter(ProductImage.product_variant_id == variant_id).count()
    if current_count >= 8:
        raise ValueError("Each variant supports at most 8 images.")

    same_position = (
        db.query(ProductImage)
        .filter(
            ProductImage.product_variant_id == variant_id,
            ProductImage.position == position,
        )
        .first()
    )
    if same_position:
        raise ValueError("This position is already in use for the variant.")

    image = ProductImage(
        product_variant_id=variant_id,
        image_url=image_url,
        position=position,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def get_image(db: Session, image_id: int) -> ProductImage | None:
    return db.query(ProductImage).filter(ProductImage.id == image_id).first()


def update_variant_image(
    db: Session,
    image: ProductImage,
    *,
    image_url: str | None = None,
    position: int | None = None,
) -> ProductImage:
    if position is not None:
        if position < 1 or position > 8:
            raise ValueError("Position must be between 1 and 8.")
        same_position = (
            db.query(ProductImage)
            .filter(
                ProductImage.product_variant_id == image.product_variant_id,
                ProductImage.position == position,
                ProductImage.id != image.id,
            )
            .first()
        )
        if same_position:
            raise ValueError("This position is already in use for the variant.")
        image.position = position
    if image_url is not None:
        image.image_url = image_url

    db.commit()
    db.refresh(image)
    return image


def delete_variant_image(db: Session, image: ProductImage) -> None:
    db.delete(image)
    db.commit()
