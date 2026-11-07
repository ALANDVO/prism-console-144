from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./prism.db"
    
    # Health check settings
    # Encryption key for API keys (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    encryption_key: str = ""
    health_check_interval_seconds: int = 300  # 5 minutes
    health_check_timeout_seconds: int = 10
    health_check_concurrency: int = 5
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
