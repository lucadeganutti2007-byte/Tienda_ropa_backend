from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = Field(validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
