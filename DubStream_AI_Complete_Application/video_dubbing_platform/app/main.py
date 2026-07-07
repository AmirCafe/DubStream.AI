from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sentry_sdk
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.db.session import init_db
from monitoring.prometheus_metrics import MetricsMiddleware

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Setup Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting DubStream AI in {settings.ENVIRONMENT} mode")
    init_db()
    yield
    logger.info("Shutting down DubStream AI")

app = FastAPI(
    title="DubStream AI - Video Dubbing SaaS",
    description="Production-grade AI video translation and dubbing platform",
    version="2.0.0",
    openapi_url="/api/openapi.json" if settings.ENABLE_API_DOCS else None,
    docs_url="/api/docs" if settings.ENABLE_API_DOCS else None,
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics middleware
app.add_middleware(MetricsMiddleware)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )

@app.get("/health")
@limiter.limit("1000/minute")
async def health(request: Request):
    return {"status": "ok", "service": "DubStream AI", "environment": settings.ENVIRONMENT}

@app.get("/metrics")
async def metrics():
    from prometheus_client import CollectorRegistry, generate_latest
    return generate_latest()

logger.info("DubStream AI initialized successfully")
