from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
video_uploads_total = Counter("dubstream_video_uploads_total", "Total videos uploaded")
video_processing_duration = Histogram("dubstream_video_processing_seconds", "Video processing duration")
active_jobs = Gauge("dubstream_active_jobs", "Currently processing jobs")
errors_total = Counter("dubstream_errors_total", "Total errors", ["type"])
api_requests_total = Counter("dubstream_api_requests_total", "API requests", ["method", "endpoint"])
api_response_time = Histogram("dubstream_api_response_time_seconds", "API response time", ["method", "endpoint"])

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "")
        method = scope.get("method", "")
        start_time = time.time()
        
        api_requests_total.labels(method=method, endpoint=path).inc()
        
        async def send_with_metrics(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                api_response_time.labels(method=method, endpoint=path).observe(duration)
            await send(message)
        
        await self.app(scope, receive, send_with_metrics)
