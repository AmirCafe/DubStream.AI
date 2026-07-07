# DubStream AI - API Documentation

## Authentication

All endpoints except `/health` require JWT authentication.

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

## Jobs

### Upload Video
```http
POST /api/jobs/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary video data>
target_language: "es"
voice_id: (optional)

Response: 202 Accepted
{
  "job_id": "uuid",
  "status": "pending",
  "estimated_time": 120
}
```

### Get Job Status
```http
GET /api/jobs/{job_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 50,
  "current_step": "synthesizing_voice",
  "started_at": "2024-01-01T00:00:00Z",
  "estimated_completion": "2024-01-01T00:02:00Z",
  "steps": [
    { "step": 1, "name": "ingest", "status": "completed" },
    { "step": 2, "name": "extract_audio", "status": "completed" },
    { "step": 3, "name": "transcribe", "status": "completed" },
    { "step": 4, "name": "translate", "status": "in_progress" },
    { "step": 5, "name": "synthesize", "status": "pending" }
  ]
}
```

### List Jobs
```http
GET /api/jobs?limit=10&offset=0
Authorization: Bearer <token>

Response: 200 OK
{
  "jobs": [...],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

### Download Video
```http
GET /api/jobs/{job_id}/download
Authorization: Bearer <token>

Response: 200 OK (file)
Content-Type: video/mp4
Content-Disposition: attachment; filename="dubbed_video.mp4"
<binary video data>
```

## Payments

### Get Subscription Plans
```http
GET /api/payments/plans

Response: 200 OK
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price": 0,
      "stripe_price_id": null,
      "features": {
        "monthly_credits": 10,
        "max_video_length": 600,
        "concurrent_jobs": 1
      }
    },
    {
      "id": "pro",
      "name": "Pro",
      "price": 2999,
      "stripe_price_id": "price_xxx",
      "features": {
        "monthly_credits": 500,
        "max_video_length": 3600,
        "concurrent_jobs": 3
      }
    }
  ]
}
```

### Create Subscription
```http
POST /api/payments/subscribe
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_id": "pro",
  "payment_method": "pm_xxx"
}

Response: 201 Created
{
  "subscription_id": "sub_xxx",
  "status": "active",
  "current_period_start": "2024-01-01T00:00:00Z",
  "current_period_end": "2024-02-01T00:00:00Z",
  "client_secret": "pi_xxx_secret_xxx"
}
```

### Cancel Subscription
```http
DELETE /api/payments/subscriptions/{subscription_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "subscription_id": "sub_xxx",
  "status": "canceled",
  "canceled_at": "2024-01-15T10:30:00Z"
}
```

## Webhooks

### Stripe Webhook
```http
POST /api/payments/webhook
Stripe-Signature: <signature>

# Automatically handles:
# - customer.subscription.created
# - customer.subscription.updated
# - customer.subscription.deleted
# - invoice.paid
# - invoice.payment_failed
```

## WebSocket

### Real-time Job Updates
```javascript
const socket = new WebSocket(
  `ws://localhost:8000/ws/jobs/{job_id}?token={token}`
);

socket.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  // {
  //   "job_id": "uuid",
  //   "status": "processing",
  //   "progress": 75,
  //   "current_step": "rendering_video"
  // }
});
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "errors": {
    "target_language": "Unsupported language"
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An internal error occurred",
  "request_id": "req_xxx"
}
```

## Rate Limiting

Default: 100 requests per 60 seconds per IP

When limit exceeded:
- Status: 429
- Header: `X-RateLimit-Remaining: 0`
- Header: `X-RateLimit-Reset: 1609459200`

## Pagination

All list endpoints support:
- `limit`: Items per page (max 100)
- `offset`: Number of items to skip
- `sort`: Field to sort by
- `order`: asc or desc

## Status Codes

- 200: Success
- 201: Created
- 202: Accepted (async processing)
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden (CSRF, rate limit, etc)
- 404: Not found
- 429: Rate limited
- 500: Server error

## Base URL

Development: `http://localhost:8000`
Production: `https://api.dubstream.com`

