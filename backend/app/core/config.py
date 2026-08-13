import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Fireflies Clone API"
    
    # Database configuration (env: DATABASE_URL or DB_URI, default to local SQLite)
    DATABASE_URL: str = os.getenv("DATABASE_URL") or os.getenv("DB_URI") or "sqlite:///./meetings.db"
    
    # Strip double quotes if loaded from env
    if DATABASE_URL.startswith('"') and DATABASE_URL.endswith('"'):
        DATABASE_URL = DATABASE_URL[1:-1]
        
    # Turso Auth Token
    TURSO_AUTH_TOKEN: Optional[str] = os.getenv("TURSO_AUTH_TOKEN") or os.getenv("AUTH_TOKEN")
    
    # JWT security configurations
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # Default to 24 hours

settings = Settings()
