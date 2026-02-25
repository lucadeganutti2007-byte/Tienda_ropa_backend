from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProductImageBase(BaseModel):
    image_url: str = Field(min_length=1, max_length=1024)
    position: int = Field(ge=1, le=8)


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    image_url: str | None = Field(default=None, min_length=1, max_length=1024)
    position: int | None = Field(default=None, ge=1, le=8)


class ProductImageRead(ProductImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_variant_id: int


class ProductVariantBase(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    size: str = Field(min_length=1, max_length=50)
    color: str = Field(min_length=1, max_length=50)
    price_override: Decimal | None = None
    stock: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    images: list[ProductImageCreate] = Field(default_factory=list)

    @field_validator("images")
    @classmethod
    def validate_images_limit(cls, value: list[ProductImageCreate]) -> list[ProductImageCreate]:
        if len(value) > 8:
            raise ValueError("Each variant supports at most 8 images.")
        return value

    @model_validator(mode="after")
    def validate_unique_positions(self) -> "ProductVariantCreate":
        positions = [img.position for img in self.images]
        if len(positions) != len(set(positions)):
            raise ValueError("Image positions must be unique per variant.")
        return self


class ProductVariantUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    size: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, min_length=1, max_length=50)
    price_override: Decimal | None = None
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductVariantRead(ProductVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    images: list[ProductImageRead] = Field(default_factory=list)


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(gt=0)
    category_id: int = Field(gt=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    variants: list[ProductVariantRead] = Field(default_factory=list)
