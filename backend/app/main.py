"""FastAPI application entry point for BBG Rebate Processing Tool."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db, AsyncSessionLocal
from app.routers import lookup, upload, rules, settings as settings_router
from app.services.rule_migration import run_migration
# Import models to ensure they're registered with SQLAlchemy
from app.models.settings import Settings, ColumnSettings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize database
    await init_db()

    # Run rule migration to convert existing rules to nested format
    async with AsyncSessionLocal() as db:
        await run_migration(db)

    yield
    # Shutdown: Close database connections
    await close_db()


app = FastAPI(
    title="BBG Rebate Processing API",
    description="API for processing quarterly rebate Excel files",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lookup.router)
app.include_router(upload.router)
app.include_router(rules.router)
app.include_router(settings_router.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "BBG Rebate Processing API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "api": "running",
            "file_processing": "ready",
        },
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "error": str(exc) if settings.DEBUG else "Internal server error",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        timeout_keep_alive=settings.UPLOAD_TIMEOUT_SECONDS,
    )
