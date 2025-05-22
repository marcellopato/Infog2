from pydantic import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Lu Estilo API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENTRY_DSN: Optional[str] = None
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v17.0"
    WHATSAPP_TOKEN: str = "YOUR_WHATSAPP_TOKEN"
    WHATSAPP_PHONE_ID: str = "YOUR_PHONE_ID"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
