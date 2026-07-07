from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
import uuid

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/upload")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Video uploaded successfully"
    }

@router.get("/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 50,
        "current_step": "translating_audio"
    }

@router.get("")
async def list_jobs(db: Session = Depends(get_db)):
    return {
        "jobs": [],
        "total": 0
    }
