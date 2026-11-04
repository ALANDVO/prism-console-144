from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./prism.db"
    
    # Health check settings
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
