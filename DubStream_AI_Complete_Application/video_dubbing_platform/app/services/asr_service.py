"""
ASR Service - Automatic Speech Recognition using Faster-Whisper
Transcribes audio to text with language detection
"""

import logging
import os
from typing import Tuple, List, Dict
from faster_whisper import WhisperModel
import numpy as np

logger = logging.getLogger(__name__)


class ASRService:
    """Handles speech-to-text transcription using Faster-Whisper"""
    
    _model_cache = {}
    
    def __init__(self, model_size: str = "medium", device: str = "auto", compute_type: str = "float32"):
        """
        Initialize ASR Service
        
        Args:
            model_size: tiny, base, small, medium, large
            device: cuda, cpu, auto
            compute_type: int8, float16, float32
        """
        self.model_size = model_size
        self.device = device if device != "auto" else self._detect_device()
        self.compute_type = compute_type
        self.model = None
        
    @staticmethod
    def _detect_device() -> str:
        """Auto-detect GPU availability"""
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except:
            return "cpu"
    
    def _get_model(self):
        """Load model with caching"""
        cache_key = f"{self.model_size}_{self.device}_{self.compute_type}"
        
        if cache_key not in self._model_cache:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root="/models/whisper"
                )
                self._model_cache[cache_key] = self.model
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
        
        return self._model_cache[cache_key]
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: ISO 639-1 language code (e.g., 'en', 'ar', 'hi')
        
        Returns:
            {
                "text": "Transcribed text",
                "language": "detected_language",
                "confidence": 0.95,
                "segments": [
                    {"start": 0.0, "end": 2.5, "text": "Hello world"},
                    ...
                ]
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        model = self._get_model()
        
        try:
            segments, info = model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                patience=2.0
            )
            
            # Collect all segments
            all_segments = []
            full_text = []
            
            for segment in segments:
                all_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "confidence": segment.confidence
                })
                full_text.append(segment.text.strip())
            
            result = {
                "text": " ".join(full_text),
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": all_segments,
                "duration": info.duration
            }
            
            logger.info(f"Transcription complete: {info.language} ({len(all_segments)} segments)")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def detect_language(self, audio_path: str) -> Tuple[str, float]:
        """
        Detect language of audio file
        
        Returns:
            (language_code, confidence)
        """
        logger.info(f"Detecting language: {audio_path}")
        model = self._get_model()
        
        try:
            _, info = model.transcribe(audio_path)
            return info.language, info.language_probability
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            raise
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        # Whisper supports 99 languages
        languages = [
            'en', 'zh', 'de', 'es', 'ru', 'ko', 'fr', 'ja', 'pt', 'tr',
            'pl', 'ca', 'nl', 'ar', 'sv', 'it', 'id', 'hi', 'fi', 'vi',
            'he', 'uk', 'el', 'ms', 'cs', 'ro', 'da', 'hu', 'ta', 'no',
            'th', 'ur', 'hr', 'bg', 'lt', 'la', 'mi', 'my', 'sl', 'sk',
            'te', 'fa', 'lv', 'bn', 'sr', 'az', 'hy', 'et', 'ml', 'mk',
            'tl', 'kk', 'sq', 'sw', 'gl', 'mr', 'pa', 'gu', 'kn', 'or',
            'rw', 'af', 'mt', 'am', 'eo', 'fr_ca', 'hu', 'cs'
        ]
        return languages
