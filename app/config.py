from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # App config
    PROJECT_NAME: str = "API Gestion Portfolio"
    SECRET_KEY: str = "supersecretkey" # Se sobreescribe con .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # DB config
    DATABASE_URL: str = "sqlite:///./db_gestion.sqlite"
    
    # Environment config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
