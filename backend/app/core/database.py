from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

db_url = settings.DATABASE_URL

# Resolve database URL dialect issues
if db_url.startswith("libsql://"):
    db_url = db_url.replace("libsql://", "sqlite+libsql://")

# Ensure secure=true and authToken are handled for remote Turso connections
if db_url.startswith("sqlite+libsql://"):
    # Append secure=true to prevent 308 Permanent Redirect issues
    if "secure=true" not in db_url:
        if "?" in db_url:
            db_url += "&secure=true"
        else:
            db_url += "/?secure=true"
            
    # Append authToken from settings if available and not already in connection string
    auth_token = settings.TURSO_AUTH_TOKEN
    if auth_token and "authToken" not in db_url:
        db_url += f"&authToken={auth_token}"

# Double check if we can actually load the dialect and have credentials
if "libsql" in db_url:
    try:
        # If we have a remote libsql URL but no token is provided, raise an error to trigger the SQLite fallback
        # (Since remote Turso databases require authentication)
        if not settings.TURSO_AUTH_TOKEN and "authToken" not in db_url:
            raise ValueError("TURSO_AUTH_TOKEN is not set in environment variables.")
            
        from sqlalchemy.dialects import registry
        registry.load("sqlite.libsql")
    except Exception as e:
        # Fallback to local SQLite if dialect is missing or auth token is not configured
        print(f"Warning: {e} Falling back to local SQLite database (meetings.db).")
        db_url = "sqlite:///./meetings.db"

# For SQLite (including libsql local connection), we need connect_args check_same_thread
if db_url.startswith("sqlite") and not db_url.startswith("sqlite+libsql"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
