from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    APP_NAME: str = "Enhanced Purview CLI API"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Azure Purview settings
    PURVIEW_ACCOUNT_NAME: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    PURVIEW_ENDPOINT: Optional[str] = None
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./purview_cli.db"
    
    # Redis settings for caching and WebSocket
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: Path = Path("uploads")
      # Rate limiting settings
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 10
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_EXCLUSION_PATHS: List[str] = ["/health", "/metrics", "/docs", "/openapi.json"]
    
    # Background task settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Monitoring settings
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # WebSocket settings
    WS_CONNECTION_TIMEOUT: int = 600  # 10 minutes
    WS_HEARTBEAT_INTERVAL: int = 30   # 30 seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(exist_ok=True)
