from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Clothing Store API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "development_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/clothing_store"

    # MercadoPago
    MP_ACCESS_TOKEN: str = ""
    MP_PUBLIC_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
