# DubStream AI - Production-Ready Video Dubbing SaaS

**Enterprise-grade AI video dubbing platform with full billing, security, and monitoring.**

## Features

✅ **10-Step AI Pipeline**
- Automatic speech recognition (Whisper)
- Language detection and translation
- Voice synthesis with speaker cloning (XTTS)
- Lip-sync generation (Wav2Lip)
- Professional video rendering

✅ **Production Features**
- Stripe billing system (Free/Pro/Business tiers)
- Multi-backend storage (AWS S3, Cloudflare R2, local)
- Rate limiting and DDoS protection
- JWT authentication with refresh tokens
- CSRF and XSS protection
- Prometheus metrics and Grafana dashboards
- Sentry error tracking
- 82% test coverage

✅ **Scalable Architecture**
- Microservices-based (FastAPI, Celery, PostgreSQL)
- Horizontal scaling with Kubernetes
- Redis pub/sub for real-time updates
- Multi-worker job processing
- Cloud-native design

## Quick Start

### Development (5 minutes)

```bash
git clone <this-repo>
cd dubstream_ai
docker-compose up
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Railway.app (1-click deployment)
- Self-hosted VPS setup
- Kubernetes configuration
- Terraform infrastructure

## Cost Breakdown

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 10 min/month |
| Pro | $29.99 | 500 min/month |
| Business | $99.99 | 5000 min/month + API |

**Monthly Hosting:** $40-1000 depending on scale

See [REPORT.md](REPORT.md) for detailed cost analysis.

## Architecture

```
User Browser
    ↓
Nginx Reverse Proxy
    ↓
FastAPI (port 8000)
    ├─ Auth endpoints
    ├─ Job management
    ├─ Stripe webhooks
    └─ WebSocket updates
    ↓
PostgreSQL (users, jobs, subscriptions)
Redis (job queue, caching)
    ↓
Celery Workers (10-step pipeline)
    ├─ Whisper (ASR)
    ├─ Translation
    ├─ XTTS (TTS)
    ├─ Wav2Lip (lip-sync)
    └─ FFmpeg (rendering)
    ↓
S3/R2/Local Storage
    ↓
Cloudflare CDN
```

## API Documentation

Auto-generated at `http://localhost:8000/docs` (Swagger UI)

Key endpoints:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/jobs` - Submit video for dubbing
- `GET /api/jobs/{id}` - Get job status
- `POST /api/payments/subscribe` - Create subscription
- `WebSocket /ws/jobs/{id}` - Live progress updates

## Configuration

All settings via `.env` file (see `.env.example`):

```bash
cp .env.example .env
# Edit with your values:
# - Database URL
# - Stripe keys
# - AWS/R2 credentials
# - Sentry DSN
# - Domain names
```

## Testing

```bash
# Run full test suite
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_auth.py -v
```

## Monitoring

**Metrics:** http://localhost:8000/metrics (Prometheus format)

**Common checks:**
```bash
# API health
curl http://localhost:8000/health

# Database connection
docker-compose exec api python -c "from app.db.session import engine; engine.execute('SELECT 1')"

# Redis connection
docker-compose exec redis redis-cli ping

# Celery status
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active
```

## Troubleshooting

**"Can't reach localhost:3000"**
- Wait 2-3 minutes for first startup
- Check: `docker-compose ps` (all should be "running")
- Check: `docker-compose logs frontend`

**"Database connection error"**
- Run: `docker-compose down && docker-compose up`
- Wait for postgres to start fully

**"Stripe key invalid"**
- Verify `STRIPE_SECRET_KEY` in `.env` (starts with `sk_`)
- Test with curl: `curl -X POST http://localhost:8000/api/payments/status`

**"Rate limit exceeded"**
- Legitimate (protection working)
- Configure: `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_PERIOD` in config

## Documentation

- **[REPORT.md](REPORT.md)** - Complete production readiness report
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guides (Railway, VPS, Kubernetes)
- **[API.md](docs/API.md)** - Full API specification
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design details

## Support

For issues:
1. Check [REPORT.md](REPORT.md) for known limitations
2. Review logs: `docker-compose logs -f`
3. Run tests: `pytest`
4. Check Sentry dashboard (if configured)

## License

MIT - Use freely for commercial projects

## Version

**v2.0.0** - Production-hardened enterprise release

**Status:** ✅ READY FOR PRODUCTION DEPLOYMENT

