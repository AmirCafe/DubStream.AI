"""
Speaker Diarization Service - Using pyannote.audio
Detects and segments speech by different speakers
"""

import logging
import os
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class SpeakerDiarizationService:
    """Handles speaker diarization using pyannote.audio"""
    
    _model_cache = {}
    
    def __init__(self, device: str = "auto"):
        """
        Initialize Speaker Diarization Service
        
        Args:
            device: 'cuda' or 'cpu'
        """
        self.device = device if device != "auto" else self._detect_device()
        self.model = None
        self.available = self._check_availability()
    
    @staticmethod
    def _detect_device() -> str:
        """Auto-detect GPU availability"""
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except:
            return "cpu"
    
    def _check_availability(self) -> bool:
        """Check if pyannote.audio is available"""
        try:
            import pyannote.audio
            logger.info("pyannote.audio is available")
            return True
        except ImportError:
            logger.warning("pyannote.audio not installed")
            return False
    
    def _get_model(self):
        """Load model with caching"""
        cache_key = f"diarization_{self.device}"
        
        if cache_key not in self._model_cache:
            logger.info(f"Loading diarization model on {self.device}")
            try:
                from pyannote.audio import Pipeline
                
                # Use pretrained model
                pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.0",
                    use_auth_token=False  # Use public model
                )
                
                # Move to device
                pipeline.to(self.device)
                
                self._model_cache[cache_key] = pipeline
                logger.info("Diarization model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load diarization model: {e}")
                self.available = False
                return None
        
        return self._model_cache[cache_key]
    
    def diarize(self, audio_path: str) -> Optional[Dict]:
        """
        Perform speaker diarization on audio
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Diarization result with speaker segments
        """
        if not self.available:
            logger.warning("Diarization not available, skipping")
            return None
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio not found: {audio_path}")
            return None
        
        logger.info(f"Performing speaker diarization: {audio_path}")
        
        try:
            pipeline = self._get_model()
            if pipeline is None:
                return None
            
            # Run diarization
            diarization = pipeline(audio_path)
            
            # Convert to segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    'speaker': speaker,
                    'start': turn.start,
                    'end': turn.end,
                    'duration': turn.end - turn.start
                })
            
            result = {
                'segments': segments,
                'num_speakers': len(set(s['speaker'] for s in segments))
            }
            
            logger.info(f"Diarization complete: {result['num_speakers']} speakers, {len(segments)} segments")
            return result
            
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            return None
    
    def map_speakers_to_segments(self, audio_segments: List[Dict], diarization_result: Dict) -> List[Dict]:
        """
        Map diarization results to transcription segments
        
        Args:
            audio_segments: Transcription segments with timing
            diarization_result: Diarization result
        
        Returns:
            Segments with speaker information added
        """
        if diarization_result is None:
            logger.warning("No diarization result, skipping speaker mapping")
            return audio_segments
        
        logger.info(f"Mapping {len(audio_segments)} segments to speakers")
        
        dia_segments = diarization_result.get('segments', [])
        
        for segment in audio_segments:
            segment_start = segment['start']
            segment_end = segment['end']
            segment_middle = (segment_start + segment_end) / 2
            
            # Find speaker at segment midpoint
            speaker = "unknown"
            for dia_seg in dia_segments:
                if dia_seg['start'] <= segment_middle <= dia_seg['end']:
                    speaker = dia_seg['speaker']
                    break
            
            segment['speaker'] = speaker
        
        logger.info("Speaker mapping complete")
        return audio_segments
    
    def get_speaker_segments(self, diarization_result: Dict) -> Dict[str, List]:
        """
        Get timeline segments for each speaker
        
        Args:
            diarization_result: Diarization result
        
        Returns:
            Dictionary mapping speaker to list of time segments
        """
        if diarization_result is None:
            return {}
        
        speaker_segments = {}
        for segment in diarization_result.get('segments', []):
            speaker = segment['speaker']
            if speaker not in speaker_segments:
                speaker_segments[speaker] = []
            
            speaker_segments[speaker].append({
                'start': segment['start'],
                'end': segment['end']
            })
        
        return speaker_segments
