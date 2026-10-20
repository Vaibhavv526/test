"""
FastAPI Application Entry Point for Agentic Dating Demo.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import init_db, get_db, ProfileDB, DateSimulationDB
from app.api import profiles, dates, rankings
from app.agent import ANTHROPIC_MODEL, get_anthropic_client
from app.seed_data import seed_database_with_25_profiles

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agentic_dating")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed initial synthetic profiles if empty
    logger.info("Initializing Agentic Dating SQLite Database...")
    init_db()

    # Auto-seed initial 25 synthetic profiles if database is fresh
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        count = db.query(ProfileDB).count()
        if count == 0:
            logger.info("Empty database detected. Seeding 25 diverse synthetic profiles...")
            seed_database_with_25_profiles(db)
        db.close()
    except Exception as e:
        logger.warning(f"Auto-seed check notice: {e}")

    yield
    logger.info("Shutting down Agentic Dating Backend...")


app = FastAPI(
    title="Agentic Dating AI Platform",
    description="Simulating human romantic compatibility through autonomous LLM persona agents.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration reading from ALLOWED_ORIGINS env var with localhost fallback
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if allowed_origins_env:
    allow_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
else:
    allow_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

allow_credentials = False if "*" in allow_origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(profiles.router)
app.include_router(dates.router)
app.include_router(rankings.router)


@app.get("/api/status")
def get_system_status(db: Session = Depends(get_db)):
    """Health and configuration status endpoint."""
    has_anthropic_client = get_anthropic_client() is not None
    profile_count = db.query(ProfileDB).count()
    simulation_count = db.query(DateSimulationDB).count()
    self_reported_count = db.query(ProfileDB).filter(ProfileDB.source == "self-reported").count()
    synthetic_count = db.query(ProfileDB).filter(ProfileDB.source == "synthetic").count()

    return {
        "status": "healthy",
        "llm_engine": {
            "provider": "Anthropic Claude",
            "model": ANTHROPIC_MODEL,
            "has_api_key": has_anthropic_client,
            "mode": "live-claude" if has_anthropic_client else "smart-simulation-fallback"
        },
        "stats": {
            "total_profiles": profile_count,
            "self_reported": self_reported_count,
            "synthetic": synthetic_count,
            "simulated_dates": simulation_count
        }
    }


@app.post("/api/seed")
def seed_profiles_endpoint(db: Session = Depends(get_db)):
    """Explicitly trigger/re-seed the 25 diverse synthetic profiles."""
    added = seed_database_with_25_profiles(db)
    return {
        "status": "success",
        "message": f"Successfully seeded {added} synthetic profiles.",
        "total_profiles": db.query(ProfileDB).count()
    }
