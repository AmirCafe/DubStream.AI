from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "dubstream",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

celery_app.conf.beat_schedule = {
    "cleanup-old-videos": {
        "task": "app.tasks.pipeline_tasks.cleanup_old_videos",
        "schedule": 86400.0,  # Daily
    },
    "requeue-stuck-jobs": {
        "task": "app.tasks.pipeline_tasks.requeue_stuck_jobs",
        "schedule": 3600.0,  # Hourly
    },
}
