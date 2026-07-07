from app.core.celery_app import celery_app
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def step1_ingest_video(self, job_id: str, video_url: str):
    """Step 1: Download or ingest video"""
    try:
        logger.info(f"Job {job_id}: Ingesting video from {video_url}")
        return {"job_id": job_id, "step": 1, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 1 failed - {str(exc)}")
        raise self.retry(exc=exc, countdown=60)

@celery_app.task(bind=True)
def step2_extract_audio(self, job_id: str):
    """Step 2: Extract audio from video"""
    try:
        logger.info(f"Job {job_id}: Extracting audio")
        return {"job_id": job_id, "step": 2, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 2 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step3_transcribe(self, job_id: str):
    """Step 3: Transcribe audio to text"""
    try:
        logger.info(f"Job {job_id}: Transcribing audio")
        return {"job_id": job_id, "step": 3, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 3 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step4_translate(self, job_id: str, target_language: str):
    """Step 4: Translate transcription"""
    try:
        logger.info(f"Job {job_id}: Translating to {target_language}")
        return {"job_id": job_id, "step": 4, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 4 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step5_align_timestamps(self, job_id: str):
    """Step 5: Align timestamps"""
    try:
        logger.info(f"Job {job_id}: Aligning timestamps")
        return {"job_id": job_id, "step": 5, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 5 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step6_synthesize_voice(self, job_id: str):
    """Step 6: Synthesize voice"""
    try:
        logger.info(f"Job {job_id}: Synthesizing voice")
        return {"job_id": job_id, "step": 6, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 6 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step7_clone_voice(self, job_id: str):
    """Step 7: Clone voice"""
    try:
        logger.info(f"Job {job_id}: Cloning voice")
        return {"job_id": job_id, "step": 7, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 7 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step8_lipsync(self, job_id: str):
    """Step 8: Generate lip-sync (optional)"""
    try:
        if not settings.LIPSYNC_ENABLED:
            logger.info(f"Job {job_id}: Lip-sync disabled, skipping")
            return {"job_id": job_id, "step": 8, "status": "skipped"}
        
        logger.info(f"Job {job_id}: Generating lip-sync")
        return {"job_id": job_id, "step": 8, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 8 failed - {str(exc)}")
        # Don't fail job if lip-sync fails
        return {"job_id": job_id, "step": 8, "status": "skipped", "error": str(exc)}

@celery_app.task(bind=True)
def step9_render_video(self, job_id: str):
    """Step 9: Render final video"""
    try:
        logger.info(f"Job {job_id}: Rendering video")
        return {"job_id": job_id, "step": 9, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 9 failed - {str(exc)}")
        raise

@celery_app.task(bind=True)
def step10_upload_storage(self, job_id: str):
    """Step 10: Upload to storage"""
    try:
        logger.info(f"Job {job_id}: Uploading to storage")
        return {"job_id": job_id, "step": 10, "status": "completed"}
    except Exception as exc:
        logger.error(f"Job {job_id}: Step 10 failed - {str(exc)}")
        raise

@celery_app.task
def cleanup_old_videos():
    """Maintenance: Clean up old videos"""
    logger.info("Running cleanup of old videos")

@celery_app.task
def requeue_stuck_jobs():
    """Maintenance: Requeue stuck jobs"""
    logger.info("Checking for stuck jobs")
