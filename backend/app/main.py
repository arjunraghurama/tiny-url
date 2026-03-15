import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.cache import cache
from app.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
    - Creates database tables if they don't exist
    - Connects to Valkey cache

    Shutdown:
    - Closes cache connection
    - Disposes database engine
    """
    # Startup
    logger.info("Starting Tiny URL service...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

    await cache.connect()
    logger.info("All services initialized")

    yield

    # Shutdown
    await cache.close()
    await engine.dispose()
    logger.info("Tiny URL service shut down")


app = FastAPI(
    title="Tiny URL API",
    description="A URL shortening service — a system design learning project",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)
