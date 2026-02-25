from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)
    role: str = Field(default="customer", pattern="^(admin|customer)$")


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=60)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)
    role: str | None = Field(default=None, pattern="^(admin|customer)$")


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
