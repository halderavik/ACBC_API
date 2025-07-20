from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import byo, screening, tournament
from .database import engine, Base
import os

app = FastAPI(
    title="ACBC API",
    description="Adaptive Choice-Based Conjoint Analysis API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(byo.router, prefix="/api/byo-config", tags=["BYO"])
app.include_router(screening.router, prefix="/api/screening", tags=["Screening"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["Tournament"])

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "ACBC API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Heroku."""
    return {"status": "healthy"}

@app.post("/health")
async def health_check_post():
    """Health check endpoint for Heroku (POST method support)."""
    return {"status": "healthy"}

