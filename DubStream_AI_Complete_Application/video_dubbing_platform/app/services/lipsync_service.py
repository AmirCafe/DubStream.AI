"""
Lip-Sync Service - Wav2Lip integration
Synchronizes mouth movement with audio using Wav2Lip
"""

import logging
import os
import subprocess
from typing import Optional
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class LipsyncService:
    """Handles lip-sync generation using Wav2Lip"""
    
    def __init__(self, checkpoint_path: str = "/opt/Wav2Lip/checkpoints/wav2lip_gan.pth",
                 repo_path: str = "/opt/Wav2Lip"):
        """
        Initialize Lip-Sync Service
        
        Args:
            checkpoint_path: Path to Wav2Lip checkpoint
            repo_path: Path to Wav2Lip repository
        """
        self.checkpoint_path = checkpoint_path
        self.repo_path = repo_path
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Wav2Lip is available"""
        if not os.path.exists(self.repo_path):
            logger.warning(f"Wav2Lip not found at {self.repo_path}")
            return False
        
        if not os.path.exists(self.checkpoint_path):
            logger.warning(f"Wav2Lip checkpoint not found at {self.checkpoint_path}")
            return False
        
        logger.info("Wav2Lip is available")
        return True
    
    def detect_faces(self, video_path: str) -> bool:
        """
        Detect if video has detectable faces
        
        Args:
            video_path: Path to video file
        
        Returns:
            True if faces detected, False otherwise
        """
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return False
        
        logger.info(f"Detecting faces in video: {video_path}")
        
        try:
            cap = cv2.VideoCapture(video_path)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            faces_found = False
            frame_count = 0
            check_frames = 30  # Check first 30 frames
            
            while frame_count < check_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    faces_found = True
                    logger.info(f"Found {len(faces)} face(s) in frame {frame_count}")
                    break
                
                frame_count += 1
            
            cap.release()
            
            if faces_found:
                logger.info("Face detection successful")
                return True
            else:
                logger.warning("No faces detected in video")
                return False
                
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return False
    
    def generate_lipsync(self, video_path: str, audio_path: str, output_path: str) -> Optional[str]:
        """
        Generate lip-synced video using Wav2Lip
        
        Args:
            video_path: Path to input video
            audio_path: Path to dubbed audio
            output_path: Path to output video
        
        Returns:
            Path to output video if successful, None otherwise
        """
        if not self.available:
            logger.warning("Wav2Lip not available, skipping lip-sync")
            return None
        
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return None
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio not found: {audio_path}")
            return None
        
        logger.info(f"Generating lip-sync: {os.path.basename(video_path)}")
        
        try:
            # Check for faces first
            if not self.detect_faces(video_path):
                logger.warning("No faces detected, skipping lip-sync")
                return None
            
            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Prepare Wav2Lip command
            cmd = [
                'python', 'inference.py',
                '--checkpoint_path', self.checkpoint_path,
                '--face', video_path,
                '--audio', audio_path,
                '--outfile', output_path,
                '--device', 'cuda',
                '--nosmooth'
            ]
            
            logger.info(f"Running Wav2Lip: {' '.join(cmd)}")
            
            # Run Wav2Lip
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Wav2Lip failed: {result.stderr}")
                # Return original video path instead of failing
                return video_path
            
            if os.path.exists(output_path):
                logger.info(f"Lip-sync successful: {output_path}")
                return output_path
            else:
                logger.warning("Lip-sync output not found")
                return video_path
                
        except subprocess.TimeoutExpired:
            logger.error("Wav2Lip processing timed out")
            return video_path
        except Exception as e:
            logger.error(f"Lip-sync generation failed: {e}")
            # Return original video instead of failing
            return video_path
    
    def skip_lipsync_gracefully(self, video_path: str) -> str:
        """
        Return original video when lip-sync is skipped
        
        Args:
            video_path: Original video path
        
        Returns:
            Original video path
        """
        logger.info("Lip-sync skipped, using original video")
        return video_path
