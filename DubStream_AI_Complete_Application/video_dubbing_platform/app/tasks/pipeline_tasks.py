"""
Celery Pipeline Tasks - 10-Step Video Dubbing Workflow
Complete integration of all AI services
"""

import logging
import os
import tempfile
from typing import Dict, Optional
from celery import shared_task
from app.core.celery_app import celery_app
from app.services.asr_service import ASRService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService
from app.services.voice_clone_service import VoiceCloneService
from app.services.lipsync_service import LipsyncService
from app.services.render_service import RenderService
from app.services.speaker_diarization_service import SpeakerDiarizationService
from app.services.storage_service import StorageService
import numpy as np

logger = logging.getLogger(__name__)

# Initialize services
asr = ASRService(model_size="medium", device="auto")
translator = TranslationService()
tts = TTSService(device="auto")
voice_cloner = VoiceCloneService()
lipsync = LipsyncService()
render = RenderService()
diarization = SpeakerDiarizationService(device="auto")


@celery_app.task(bind=True, max_retries=2)
def step1_ingest_video(self, job_id: str, video_url: str, video_path: str) -> Dict:
    """
    Step 1: Ingest and validate video
    
    Downloads from URL or validates uploaded file
    """
    try:
        logger.info(f"[Job {job_id}] Step 1: Ingesting video")
        
        # Validate video exists and is accessible
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        file_size = os.path.getsize(video_path)
        logger.info(f"[Job {job_id}] Video ingested: {file_size} bytes")
        
        return {
            "job_id": job_id,
            "step": 1,
            "status": "completed",
            "video_path": video_path,
            "video_size": file_size
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 1 failed: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=2)


@celery_app.task(bind=True)
def step2_extract_audio(self, job_id: str, video_path: str) -> Dict:
    """
    Step 2: Extract audio from video
    
    Converts video to WAV audio at 16kHz mono
    """
    try:
        logger.info(f"[Job {job_id}] Step 2: Extracting audio")
        
        # Create temp directory for job
        temp_dir = tempfile.mkdtemp(prefix=f"job_{job_id}_")
        audio_path = os.path.join(temp_dir, "audio.wav")
        speaker_ref_path = os.path.join(temp_dir, "speaker_ref.wav")
        
        # Use FFmpeg to extract audio
        import subprocess
        cmd = [
            'ffmpeg', '-i', video_path,
            '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            '-y', audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        # Extract speaker reference (first 12 seconds)
        cmd_ref = [
            'ffmpeg', '-i', audio_path,
            '-t', '12',
            '-acodec', 'pcm_s16le',
            '-y', speaker_ref_path
        ]
        
        result = subprocess.run(cmd_ref, capture_output=True, timeout=60)
        
        logger.info(f"[Job {job_id}] Audio extracted: {audio_path}")
        
        return {
            "job_id": job_id,
            "step": 2,
            "status": "completed",
            "audio_path": audio_path,
            "speaker_ref_path": speaker_ref_path,
            "temp_dir": temp_dir
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 2 failed: {e}")
        raise


@celery_app.task(bind=True)
def step3_transcribe(self, job_id: str, audio_path: str) -> Dict:
    """
    Step 3: Transcribe audio to text
    
    Uses Faster-Whisper for speech-to-text
    """
    try:
        logger.info(f"[Job {job_id}] Step 3: Transcribing audio")
        
        result = asr.transcribe(audio_path)
        
        logger.info(f"[Job {job_id}] Transcription complete: {result['language']}")
        
        return {
            "job_id": job_id,
            "step": 3,
            "status": "completed",
            "text": result['text'],
            "language": result['language'],
            "segments": result['segments']
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 3 failed: {e}")
        raise


@celery_app.task(bind=True)
def step4_translate(self, job_id: str, segments: list, source_lang: str, target_lang: str) -> Dict:
    """
    Step 4: Translate transcribed text
    
    Uses Google Translate to translate segments
    """
    try:
        logger.info(f"[Job {job_id}] Step 4: Translating {source_lang} → {target_lang}")
        
        translated_segments = translator.translate_segments(segments, source_lang, target_lang)
        translator.align_translation_to_timing(translated_segments)
        
        logger.info(f"[Job {job_id}] Translation complete: {len(translated_segments)} segments")
        
        return {
            "job_id": job_id,
            "step": 4,
            "status": "completed",
            "segments": translated_segments,
            "target_language": target_lang
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 4 failed: {e}")
        raise


@celery_app.task(bind=True)
def step5_align_timestamps(self, job_id: str, segments: list) -> Dict:
    """
    Step 5: Align timestamps to speech duration
    
    Ensures translation timing matches original speech
    """
    try:
        logger.info(f"[Job {job_id}] Step 5: Aligning timestamps")
        
        # Already done in step 4, but can add additional refinements
        for segment in segments:
            segment['original_duration'] = segment['end'] - segment['start']
        
        logger.info(f"[Job {job_id}] Timestamp alignment complete")
        
        return {
            "job_id": job_id,
            "step": 5,
            "status": "completed",
            "segments": segments
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 5 failed: {e}")
        raise


@celery_app.task(bind=True)
def step6_synthesize_voice(self, job_id: str, segments: list, target_lang: str, 
                          speaker_ref_path: Optional[str] = None) -> Dict:
    """
    Step 6: Synthesize speech from translated text
    
    Uses Coqui XTTS-v2 with voice cloning
    """
    try:
        logger.info(f"[Job {job_id}] Step 6: Synthesizing voice ({target_lang})")
        
        synthesized_segments = tts.synthesize_segments(
            segments,
            target_lang,
            speaker_reference_path=speaker_ref_path
        )
        
        logger.info(f"[Job {job_id}] Synthesis complete: {len(synthesized_segments)} segments")
        
        return {
            "job_id": job_id,
            "step": 6,
            "status": "completed",
            "segments": synthesized_segments
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 6 failed: {e}")
        raise


@celery_app.task(bind=True)
def step7_clone_voice(self, job_id: str, segments: list, speaker_ref_path: str) -> Dict:
    """
    Step 7: Apply voice cloning to synthesized speech
    
    Matches synthesized audio to original speaker voice
    """
    try:
        logger.info(f"[Job {job_id}] Step 7: Cloning voice")
        
        for segment in segments:
            if 'audio' in segment and len(segment['audio']) > 0:
                segment['audio'] = voice_cloner.clone_voice(
                    segment['audio'],
                    speaker_ref_path
                )
        
        logger.info(f"[Job {job_id}] Voice cloning complete")
        
        return {
            "job_id": job_id,
            "step": 7,
            "status": "completed",
            "segments": segments
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 7 failed: {e}")
        raise


@celery_app.task(bind=True)
def step8_lipsync(self, job_id: str, video_path: str, audio_path: str) -> Dict:
    """
    Step 8: Generate lip-sync (optional, can skip if GPU unavailable)
    
    Uses Wav2Lip for mouth movement synchronization
    """
    try:
        logger.info(f"[Job {job_id}] Step 8: Generating lip-sync (optional)")
        
        # Try Wav2Lip, but don't fail if unavailable
        output_path = tempfile.mktemp(suffix=".mp4", prefix=f"lipsync_{job_id}_")
        
        synced_video = lipsync.generate_lipsync(video_path, audio_path, output_path)
        
        if synced_video is None:
            logger.info(f"[Job {job_id}] Lip-sync skipped, using original video")
            synced_video = video_path
        else:
            logger.info(f"[Job {job_id}] Lip-sync complete")
        
        return {
            "job_id": job_id,
            "step": 8,
            "status": "skipped" if synced_video == video_path else "completed",
            "video_path": synced_video
        }
    except Exception as e:
        logger.warning(f"[Job {job_id}] Step 8 warning: {e} - continuing without lip-sync")
        
        return {
            "job_id": job_id,
            "step": 8,
            "status": "skipped",
            "video_path": video_path,
            "reason": str(e)
        }


@celery_app.task(bind=True)
def step9_render_video(self, job_id: str, video_path: str, segments: list,
                      temp_dir: str, target_lang: str) -> Dict:
    """
    Step 9: Render final dubbed video
    
    Mixes audio and creates subtitles
    """
    try:
        logger.info(f"[Job {job_id}] Step 9: Rendering final video")
        
        # Concatenate all audio segments
        import soundfile as sf
        
        all_audio = []
        for segment in segments:
            if 'audio' in segment and len(segment['audio']) > 0:
                all_audio.append(segment['audio'])
        
        if all_audio:
            concatenated = np.concatenate(all_audio)
        else:
            raise ValueError("No audio generated")
        
        # Save concatenated audio
        dubbed_audio_path = os.path.join(temp_dir, "dubbed_audio.wav")
        sf.write(dubbed_audio_path, concatenated, 24000)
        
        # Compose video with new audio
        output_video = os.path.join(temp_dir, f"dubbed_{target_lang}.mp4")
        output_path = render.compose_video(video_path, dubbed_audio_path, output_video, quality="high")
        
        if output_path is None:
            raise RuntimeError("Video composition failed")
        
        # Generate subtitles
        subtitle_path = os.path.join(temp_dir, "subtitles.srt")
        render.generate_srt_subtitles(segments, subtitle_path)
        
        # Add subtitles to video (optional)
        final_output = os.path.join(temp_dir, f"final_{target_lang}.mp4")
        final_path = render.add_subtitles(output_path, subtitle_path, final_output)
        
        logger.info(f"[Job {job_id}] Rendering complete: {final_path}")
        
        return {
            "job_id": job_id,
            "step": 9,
            "status": "completed",
            "video_path": final_path,
            "subtitle_path": subtitle_path
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 9 failed: {e}")
        raise


@celery_app.task(bind=True)
def step10_upload_storage(self, job_id: str, video_path: str, target_lang: str,
                         storage_backend: str = "local") -> Dict:
    """
    Step 10: Upload dubbed video to storage
    
    Stores final video in S3, R2, or local storage
    """
    try:
        logger.info(f"[Job {job_id}] Step 10: Uploading to storage ({storage_backend})")
        
        # Initialize storage based on backend
        if storage_backend == "s3":
            storage = StorageService(
                backend="s3",
                bucket=os.getenv("S3_BUCKET", "dubstream-videos"),
                region=os.getenv("S3_REGION", "us-east-1"),
                access_key=os.getenv("AWS_ACCESS_KEY_ID", ""),
                secret_key=os.getenv("AWS_SECRET_ACCESS_KEY", "")
            )
        elif storage_backend == "r2":
            storage = StorageService(
                backend="r2",
                bucket=os.getenv("R2_BUCKET", "dubstream-videos"),
                account_id=os.getenv("R2_ACCOUNT_ID", ""),
                access_key=os.getenv("R2_ACCESS_KEY", ""),
                secret_key=os.getenv("R2_SECRET_KEY", "")
            )
        else:
            storage = StorageService(backend="local", path="/data/videos")
        
        # Upload video
        remote_key = f"jobs/{job_id}/dubbed_{target_lang}.mp4"
        result = storage.upload_file(video_path, remote_key)
        
        if not result['success']:
            raise RuntimeError(f"Upload failed: {result.get('error')}")
        
        logger.info(f"[Job {job_id}] Upload successful: {result['url']}")
        
        return {
            "job_id": job_id,
            "step": 10,
            "status": "completed",
            "download_url": result['url'],
            "file_size": result['size'],
            "storage_backend": storage_backend
        }
    except Exception as e:
        logger.error(f"[Job {job_id}] Step 10 failed: {e}")
        raise


@celery_app.task
def cleanup_old_videos():
    """Maintenance: Clean up old temporary files"""
    logger.info("Cleanup task: Removing old temporary files")
    import shutil
    import glob
    
    # Remove temp directories older than 24 hours
    temp_base = tempfile.gettempdir()
    for temp_dir in glob.glob(f"{temp_base}/job_*"):
        try:
            import time
            if time.time() - os.path.getctime(temp_dir) > 86400:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean {temp_dir}: {e}")


@celery_app.task
def requeue_stuck_jobs():
    """Maintenance: Requeue jobs stuck in processing"""
    logger.info("Requeue task: Checking for stuck jobs")
    # This would check database and requeue jobs that haven't progressed in 30+ minutes
    # Implementation depends on database queries
    pass
