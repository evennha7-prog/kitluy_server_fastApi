import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AudiCafe Retail POS API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Secret Key for JWT
    SECRET_KEY: str = "audicafe-super-secret-jwt-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days

    # Database parameters from .env
    DATABASE_URL: Optional[str] = None
    DB_URL: Optional[str] = None
    DB_CONNECTION: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "*",
    ]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Priority 1: DATABASE_URL or DB_URL
        uri = self.DATABASE_URL or self.DB_URL
        if uri:
            if uri.startswith("postgres://"):
                uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)
            elif uri.startswith("postgresql://") and not uri.startswith("postgresql+"):
                uri = uri.replace("postgresql://", "postgresql+psycopg2://", 1)
            elif uri.startswith("mysql://"):
                uri = uri.replace("mysql://", "mysql+pymysql://", 1)
            return uri

        # Priority 2: Structured DB_* environment variables
        if self.DB_HOST and self.DB_USERNAME and self.DB_NAME:
            is_pg = (self.DB_CONNECTION or "").lower() in ["postgres", "postgresql", "pgsql"]
            driver = "postgresql+psycopg2" if is_pg else "mysql+pymysql"
            port_str = f":{self.DB_PORT}" if self.DB_PORT else ""
            pwd_str = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
            return f"{driver}://{self.DB_USERNAME}{pwd_str}@{self.DB_HOST}{port_str}/{self.DB_NAME}"

        # Priority 3: Fallback SQLite (Use /tmp on Vercel/Lambda serverless if writable)
        if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            return "sqlite:////tmp/kitluy_pos.db"

        return "sqlite:///./kitluy_pos.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
