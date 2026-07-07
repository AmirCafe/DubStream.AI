# DubStream AI - System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Pages: Home, Auth, Dashboard, Jobs, Billing, Settings  │   │
│  │  Components: Upload, JobStatus, VideoPlayer, PaymentUI  │   │
│  │  State: Redux or Context API for global state           │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────────┐
│                     API Gateway (Nginx)                          │
│        ▪ Rate limiting       ▪ SSL/TLS                           │
│        ▪ Compression         ▪ Reverse proxy                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   FastAPI Application                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Route Handlers                                            │  │
│  │  ▪ /api/auth/* - Authentication & JWT                   │  │
│  │  ▪ /api/jobs/* - Job submission & status               │  │
│  │  ▪ /api/payments/* - Stripe billing                    │  │
│  │  ▪ /ws/jobs/* - WebSocket real-time updates            │  │
│  │  ▪ /metrics - Prometheus metrics                        │  │
│  │  ▪ /health - Health check                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Middleware Layer                                          │  │
│  │  ▪ CORS validation                                       │  │
│  │  ▪ JWT authentication                                    │  │
│  │  ▪ Rate limiting                                         │  │
│  │  ▪ CSRF protection                                       │  │
│  │  ▪ Error handling                                        │  │
│  │  ▪ Logging & tracing                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Business Logic Layer                                      │  │
│  │  ▪ Payment service (Stripe integration)                 │  │
│  │  ▪ Storage service (S3/R2/Local)                        │  │
│  │  ▪ User service                                          │  │
│  │  ▪ Job orchestration                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────┬─────────────────┬──────────────┬──────────────┬─────────────┘
     │                 │              │              │
     │ Queue           │ Cache        │ Storage      │ DB
     │                 │              │              │
┌────▼────┐  ┌────────▼──┐  ┌───────▼──┐  ┌────────▼──────┐
│ Celery  │  │  Redis    │  │  S3/R2   │  │  PostgreSQL   │
│ Workers │  │  Pub/Sub  │  │ Cloudflare  │  │  Database     │
└────┬────┘  └───────────┘  │ CDN       │  │               │
     │                       └──────────┘  └───────────────┘
     │
     └─ 10-Step Pipeline:
        1. Ingest video
        2. Extract audio
        3. Transcribe (Whisper)
        4. Translate
        5. Align timestamps
        6. Synthesize voice (XTTS)
        7. Clone voice
        8. Generate lip-sync (Wav2Lip)
        9. Render video
        10. Upload to storage
```

## Technology Stack

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Styling:** Tailwind CSS + CSS-in-JS
- **State Management:** React hooks + Context API
- **HTTP Client:** Fetch API
- **Real-time:** WebSocket
- **Deployment:** Vercel, Netlify, or self-hosted

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Server:** Uvicorn
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Task Queue:** Celery 5
- **Auth:** JWT + bcrypt

### AI/ML Models
- **Speech Recognition:** faster-whisper (Whisper)
- **Text-to-Speech:** Coqui XTTS-v2
- **Translation:** Google Translate / DeepL
- **Lip-Sync:** Wav2Lip
- **Video Processing:** FFmpeg

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes (optional)
- **Reverse Proxy:** Nginx
- **SSL:** Let's Encrypt
- **Storage:** AWS S3 / Cloudflare R2 / Local FS
- **CDN:** Cloudflare / CloudFront
- **Monitoring:** Prometheus + Grafana
- **Logging:** Sentry
- **CI/CD:** GitHub Actions (example)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  hashed_password VARCHAR(255),
  full_name VARCHAR(255),
  subscription_tier VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  status VARCHAR(50),
  progress INTEGER,
  source_language VARCHAR(10),
  target_language VARCHAR(10),
  video_url TEXT,
  output_url TEXT,
  error_message TEXT,
  created_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

### Subscriptions Table
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  stripe_subscription_id VARCHAR(255),
  stripe_customer_id VARCHAR(255),
  status VARCHAR(50),
  current_period_end TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

## Data Flow

### Video Upload Flow
```
1. User uploads video file
2. Frontend sends to /api/jobs/upload
3. Backend validates file (size, format)
4. File stored in S3/R2
5. Job record created in DB
6. Celery task queued
7. WebSocket message sent to client
8. Client polls/listens for updates
```

### Processing Pipeline
```
Celery Worker receives task
    ↓
Step 1-2: Extract audio (FFmpeg)
    ↓
Step 3: Transcribe (Whisper)
    ↓
Step 4: Translate (Google/DeepL)
    ↓
Step 5-7: Synthesize & clone voice (XTTS)
    ↓
Step 8: Lip-sync (Wav2Lip, optional)
    ↓
Step 9: Render video (FFmpeg)
    ↓
Step 10: Upload to storage
    ↓
Notify user via WebSocket
```

## Scalability Considerations

### Horizontal Scaling
- **API Servers:** Load balance with Nginx/HAProxy
- **Celery Workers:** Auto-scale based on queue depth
- **Database:** Read replicas for queries
- **Cache:** Redis cluster for distributed caching

### Vertical Scaling
- **CPU:** Increase for video processing
- **Memory:** More RAM for model caching
- **GPU:** NVIDIA GPUs for TTS/lip-sync acceleration

### Database Optimization
- Index on user_id, status
- Partition jobs table by date
- Archive old completed jobs
- Connection pooling with PgBouncer

## Security Architecture

```
Internet
    ↓
Cloudflare (DDoS protection)
    ↓
Nginx (SSL/TLS, rate limiting)
    ↓
FastAPI (CORS, CSRF, auth)
    ↓
Database (encrypted passwords, encrypted connections)
    ↓
Storage (encrypted at rest, IAM roles)
```

### Authentication Flow
```
1. User enters email/password
2. Frontend sends to /api/auth/login
3. Backend verifies password with bcrypt
4. JWT token generated (signed, expires in 7 days)
5. Token stored in localStorage
6. Subsequent requests include: Authorization: Bearer <token>
7. Middleware verifies JWT signature
8. Payload contains user_id, exp, iat
```

## Deployment Options

### Development
```
docker-compose up
↓
All services locally on Docker
```

### Production (Railway)
```
GitHub → Railway → Auto-deploy
Cost: $5-20/month
```

### Production (Self-Hosted)
```
VPS (DigitalOcean, Linode, AWS)
    ├─ Docker host
    ├─ Nginx reverse proxy
    ├─ PostgreSQL (managed service)
    └─ Redis (managed service)
Cost: $40-200/month
```

### Production (Kubernetes)
```
AWS EKS / Google GKE
    ├─ API pods (auto-scaling)
    ├─ Worker pods (auto-scaling)
    ├─ CloudSQL (managed database)
    └─ Cloud Storage (managed S3)
Cost: $200-2000/month
```

## Monitoring & Observability

### Metrics
- Video processing time
- API response time
- Error rates
- Active jobs
- Storage usage
- Database connections

### Logging
- Structured JSON logs
- Request ID tracing
- Error tracking (Sentry)
- Database query logging

### Alerts
- Processing time > 30min
- Error rate > 5%
- Database unavailable
- Storage quota > 80%
- API response time p95 > 5s

