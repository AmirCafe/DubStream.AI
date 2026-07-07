"""
Render Service - FFmpeg video composition
Combines video, audio, and subtitles into final output
"""

import logging
import os
import subprocess
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)


class RenderService:
    """Handles video rendering and composition using FFmpeg"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize Render Service
        
        Args:
            ffmpeg_path: Path to ffmpeg binary
        """
        self.ffmpeg_path = ffmpeg_path
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                timeout=5
            )
            available = result.returncode == 0
            if available:
                logger.info("FFmpeg is available")
            else:
                logger.warning("FFmpeg not found")
            return available
        except Exception as e:
            logger.warning(f"FFmpeg check failed: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video information using ffprobe
        
        Args:
            video_path: Path to video file
        
        Returns:
            Dictionary with video information
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            data = json.loads(result.stdout)
            
            info = {
                'duration': float(data['format'].get('duration', 0)),
                'bitrate': int(data['format'].get('bit_rate', 0)),
                'streams': len(data['streams'])
            }
            
            logger.info(f"Video info: {info['duration']:.1f}s, {len(data['streams'])} streams")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}
    
    def compose_video(self, video_path: str, audio_path: str,
                     output_path: str, quality: str = "high") -> Optional[str]:
        """
        Compose video with new audio
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path to output video
            quality: 'low', 'medium', 'high'
        
        Returns:
            Output path if successful, None otherwise
        """
        if not self.available:
            logger.error("FFmpeg not available")
            return None
        
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return None
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio not found: {audio_path}")
            return None
        
        logger.info(f"Composing video: {os.path.basename(video_path)}")
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Quality settings
            crf_values = {'low': 28, 'medium': 23, 'high': 18}
            crf = crf_values.get(quality, 23)
            
            # FFmpeg command
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', str(crf),
                '-c:a', 'aac',
                '-b:a', '128k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                '-y',
                output_path
            ]
            
            logger.info(f"Running FFmpeg: CRF={crf}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
            
            if os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"Composition successful: {output_path} ({size_mb:.1f}MB)")
                return output_path
            else:
                logger.error("Output file not created")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg processing timed out")
            return None
        except Exception as e:
            logger.error(f"Video composition failed: {e}")
            return None
    
    def add_subtitles(self, video_path: str, subtitle_path: str,
                     output_path: str) -> Optional[str]:
        """
        Add SRT subtitles to video (burn-in)
        
        Args:
            video_path: Path to video file
            subtitle_path: Path to SRT file
            output_path: Path to output video
        
        Returns:
            Output path if successful, None otherwise
        """
        if not self.available:
            logger.error("FFmpeg not available")
            return None
        
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return None
        
        if not os.path.exists(subtitle_path):
            logger.warning(f"Subtitle file not found: {subtitle_path}")
            return video_path  # Return video without subtitles
        
        logger.info(f"Adding subtitles to video")
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Escape subtitle path for ffmpeg filter
            subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
            
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vf', f"subtitles='{subtitle_path_escaped}':force_style='FontSize=16,FontName=Arial'",
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            logger.info("Running FFmpeg subtitle filter")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode != 0:
                logger.error(f"Subtitle addition failed: {result.stderr}")
                return video_path  # Return video without subtitles
            
            if os.path.exists(output_path):
                logger.info(f"Subtitles added: {output_path}")
                return output_path
            else:
                return video_path
                
        except Exception as e:
            logger.error(f"Subtitle addition failed: {e}")
            return video_path
    
    def generate_srt_subtitles(self, segments: List[Dict], output_path: str) -> str:
        """
        Generate SRT subtitle file from segments
        
        Args:
            segments: Segments with 'start', 'end', 'text'
            output_path: Path to output SRT file
        
        Returns:
            Path to SRT file
        """
        logger.info(f"Generating subtitles: {len(segments)} segments")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        srt_content = []
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment['start'])
            end = self._format_timestamp(segment['end'])
            text = segment.get('text', '')
            
            srt_content.append(f"{i}\n{start} --> {end}\n{text}\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        
        logger.info(f"SRT file created: {output_path}")
        return output_path
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
