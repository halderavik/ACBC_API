from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import byo, screening, tournament
from .database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(byo.router, prefix="/api/byo-config", tags=["BYO"])
app.include_router(screening.router, prefix="/api/screening", tags=["Screening"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["Tournament"])