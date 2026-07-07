from fastapi import APIRouter, Request
from app.security.rate_limit import limiter

router = APIRouter()

@router.get("/health")
@limiter.limit("1000/minute")
async def health_check(request: Request):
    return {
        "status": "ok",
        "service": "DubStream AI",
        "version": "2.0.0",
        "environment": "production"
    }
