from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dubstream")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Storage
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "local")
    LOCAL_STORAGE_PATH: str = "/data/videos"
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    R2_BUCKET: str = os.getenv("R2_BUCKET", "")
    CLOUDFLARE_CDN_URL: str = os.getenv("CLOUDFLARE_CDN_URL", "")
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLIC_KEY: str = os.getenv("STRIPE_PUBLIC_KEY", "")
    
    # AI Models
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "medium")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    TTS_DEVICE: str = os.getenv("TTS_DEVICE", "cpu")
    TTS_ENGINE: str = "xtts"
    
    # Wav2Lip
    LIPSYNC_ENABLED: bool = os.getenv("LIPSYNC_ENABLED", "false").lower() == "true"
    WAV2LIP_REPO_PATH: str = "/opt/Wav2Lip"
    WAV2LIP_CHECKPOINT: str = "/opt/Wav2Lip/checkpoints/wav2lip_gan.pth"
    
    # Features
    ENABLE_API_DOCS: bool = ENVIRONMENT != "production"
    ENABLE_METRICS: bool = True
    ENABLE_PROFILING: bool = ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
