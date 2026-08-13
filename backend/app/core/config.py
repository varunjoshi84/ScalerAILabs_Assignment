import os
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "FastAPI Custom Auth"
    
    # Read DB_URI from .env, fallback to local sqlite file
    DATABASE_URL: str = os.getenv("DB_URI", "libsql://scalarai-varunjoshi84.aws-ap-south-1.turso.io")
    
    # Let's clean up quotes from the env var if present
    if DATABASE_URL.startswith('"') and DATABASE_URL.endswith('"'):
        DATABASE_URL = DATABASE_URL[1:-1]
        
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-custom-auth-key-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # Default 24 hours


settings = Settings()
