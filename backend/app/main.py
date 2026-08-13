from fastapi import FastAPI
from app.core.database import Base, engine
from app.models.user import User  # Ensure models are imported for metadata registration
from app.api.auth import router as auth_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scalar AI Labs Assignment")

# Register API routes
app.include_router(auth_router, prefix="/api")

@app.get('/')
def root():
    return {"message": "backend is running"}