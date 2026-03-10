"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .core.config import settings
from .core.db import init_db, close_db, AsyncSessionLocal
from .core.utils import redis_client
from .workers.scheduler import create_scheduler, start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    from .modules.system_settings.bootstrap import ensure_default_settings
    async with AsyncSessionLocal() as db:
        await ensure_default_settings(db)
        await db.commit()
    await redis_client.init_cache()
    await redis_client.init_jobs()
    
    # Start scheduler
    scheduler = create_scheduler()
    start_scheduler(scheduler)
    app.state.scheduler = scheduler
    
    yield
    
    # Shutdown
    shutdown_scheduler(scheduler)
    await close_db()
    await redis_client.close()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (for production)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure properly in production
    )


# Include routers
from .modules.auth import router as auth_router
from .modules.users import router as users_router
from .modules.subscriptions import router as subscriptions_router
from .modules.payments import router as payments_router
from .modules.telegram import router as telegram_router
from .modules.broadcasts import router as broadcasts_router
from .modules.schedule import router as schedule_router
from .modules.system_settings import router as system_settings_router
from .modules.admin import router as admin_router
from .modules.bot_config.router import router as bot_config_router
from .modules.bot_config.bot_api import router as bot_api_router
from .modules.miniapp.router import router as miniapp_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(payments_router, prefix="/api/payments", tags=["payments"])
app.include_router(telegram_router, prefix="/api/telegram", tags=["telegram"])
app.include_router(broadcasts_router, prefix="/api/broadcasts", tags=["broadcasts"])
app.include_router(schedule_router, prefix="/api/schedule", tags=["schedule"])
app.include_router(system_settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(bot_config_router, prefix="/api/bot", tags=["bot"])
app.include_router(bot_api_router, prefix="/api/bot", tags=["bot"])
app.include_router(miniapp_router, prefix="/api/miniapp", tags=["miniapp"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bella Subscription Platform API",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Does not require authentication.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
