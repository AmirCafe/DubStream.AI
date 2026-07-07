"""
Job Management API Routes
Submit, track, and download dubbed videos
"""

import logging
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models import User, Job
from app.tasks.pipeline_tasks import (
    step1_ingest_video, step2_extract_audio, step3_transcribe,
    step4_translate, step5_align_timestamps, step6_synthesize_voice,
    step7_clone_voice, step8_lipsync, step9_render_video, step10_upload_storage
)
from celery import chain, group
import tempfile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobCreateRequest(BaseModel):
    """Request to create a new dubbing job"""
    target_language: str
    video_url: str = None
    storage_backend: str = "local"


class JobResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    progress: int
    current_step: int
    target_language: str
    created_at: str
    download_url: str = None


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    target_language: str = "ar",
    db: Session = Depends(get_db)
):
    """
    Upload a video for dubbing
    
    Args:
        file: Video file (MP4, MOV, etc)
        target_language: Target language code (e.g., 'ar', 'es', 'fr')
    
    Returns:
        Job ID and status
    """
    try:
        # Validate language
        if not target_language or len(target_language) != 2:
            raise HTTPException(status_code=400, detail="Invalid language code")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Check file size (max 500MB)
        file_size = 0
        temp_path = None
        
        try:
            # Save uploaded file to temp directory
            temp_dir = tempfile.mkdtemp(prefix="upload_")
            temp_path = os.path.join(temp_dir, file.filename)
            
            with open(temp_path, "wb") as f:
                while True:
                    chunk = await file.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    file_size += len(chunk)
                    f.write(chunk)
                    
                    if file_size > 500 * 1024 * 1024:  # 500MB limit
                        os.remove(temp_path)
                        raise HTTPException(
                            status_code=413,
                            detail="File too large (max 500MB)"
                        )
            
            logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")
            
            # Create job record
            job_id = str(uuid.uuid4())
            job = Job(
                id=job_id,
                status="pending",
                progress=0,
                current_step=1,
                target_language=target_language,
                source_file=temp_path,
                created_at=None
            )
            db.add(job)
            db.commit()
            
            # Queue Celery pipeline
            pipeline = chain(
                step1_ingest_video.s(job_id, None, temp_path),
                step2_extract_audio.s(job_id),
                step3_transcribe.s(job_id),
                step4_translate.s(job_id, target_language),
                step5_align_timestamps.s(job_id),
                step6_synthesize_voice.s(job_id, target_language, None),
                step7_clone_voice.s(job_id),
                step8_lipsync.s(job_id),
                step9_render_video.s(job_id, target_language, temp_dir),
                step10_upload_storage.s(job_id, target_language, "local")
            )
            
            result = pipeline.apply_async()
            
            logger.info(f"Job created: {job_id} (pipeline: {result.id})")
            
            return {
                "job_id": job_id,
                "status": "pending",
                "progress": 0,
                "message": "Video uploaded. Processing will start shortly."
            }
            
        except Exception as e:
            logger.error(f"Upload processing failed: {e}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=500, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get current job status and progress
    
    Args:
        job_id: Job UUID
    
    Returns:
        Job status with progress and download URL
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Calculate progress (10 steps)
        progress = (job.current_step / 10) * 100
        
        response = {
            "job_id": job_id,
            "status": job.status,
            "progress": int(progress),
            "current_step": job.current_step,
            "target_language": job.target_language,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        
        # Add download URL if completed
        if job.status == "completed" and job.output_file:
            response["download_url"] = f"/api/jobs/{job_id}/download"
        
        # Add error if failed
        if job.status == "failed":
            response["error"] = job.error_message
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job status")


@router.get("/{job_id}/download")
async def download_video(job_id: str, db: Session = Depends(get_db)):
    """
    Download the dubbed video
    
    Args:
        job_id: Job UUID
    
    Returns:
        Video file for download
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Job not completed. Status: {job.status}"
            )
        
        if not job.output_file or not os.path.exists(job.output_file):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        logger.info(f"Downloading job {job_id}: {job.output_file}")
        
        return FileResponse(
            job.output_file,
            media_type="video/mp4",
            filename=f"dubbed_{job.target_language}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail="Download failed")


@router.get("")
async def list_jobs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    List all jobs for current user
    
    Args:
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of jobs with status
    """
    try:
        jobs = db.query(Job).offset(skip).limit(limit).all()
        total = db.query(Job).count()
        
        return {
            "jobs": [
                {
                    "job_id": job.id,
                    "status": job.status,
                    "progress": int((job.current_step / 10) * 100),
                    "target_language": job.target_language,
                    "created_at": job.created_at.isoformat() if job.created_at else None
                }
                for job in jobs
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")


@router.delete("/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """
    Delete a job and its associated files
    
    Args:
        job_id: Job UUID
    
    Returns:
        Confirmation message
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Delete associated files
        if job.source_file and os.path.exists(job.source_file):
            try:
                os.remove(job.source_file)
            except:
                pass
        
        if job.output_file and os.path.exists(job.output_file):
            try:
                os.remove(job.output_file)
            except:
                pass
        
        # Delete job record
        db.delete(job)
        db.commit()
        
        logger.info(f"Job deleted: {job_id}")
        
        return {"message": "Job deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete job")
