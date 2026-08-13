from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.auth import router as auth_router
from app.routers.meetings import router as meetings_router
from app.routers.transcripts import router as transcripts_router
from app.routers.action_items import router as action_items_router
from app.seed import seed_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables on startup
    Base.metadata.create_all(bind=engine)
    
    # 2. Run idempotent database seeding
    db = SessionLocal()
    try:
        seed_db(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()
        
    yield

app = FastAPI(
    title="Fireflies.ai Clone API",
    description="Backend API for meeting transcription, notes, and action items management.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(meetings_router)
app.include_router(transcripts_router)
app.include_router(action_items_router)

@app.get("/")
def root():
    return {
        "message": "Fireflies.ai Clone API is running",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }