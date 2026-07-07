"""
TTS Service - Text-to-Speech using Coqui XTTS-v2
Generates voice audio from translated text with voice cloning support
"""

import logging
import os
from typing import List, Dict, Optional
import numpy as np
import soundfile as sf
from TTS.api import TTS

logger = logging.getLogger(__name__)


class TTSService:
    """Handles text-to-speech synthesis using Coqui XTTS-v2"""
    
    _model_cache = {}
    
    # Supported languages for XTTS-v2
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'pl': 'Polish',
        'tr': 'Turkish',
        'ru': 'Russian',
        'nl': 'Dutch',
        'ja': 'Japanese',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'ko': 'Korean',
        'hu': 'Hungarian',
        'cs': 'Czech'
    }
    
    def __init__(self, device: str = "auto", gpu_memory: int = 4):
        """
        Initialize TTS Service
        
        Args:
            device: 'cuda' or 'cpu'
            gpu_memory: GPU memory in GB
        """
        self.device = device if device != "auto" else self._detect_device()
        self.gpu_memory = gpu_memory
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
        cache_key = f"xtts_v2_{self.device}"
        
        if cache_key not in self._model_cache:
            logger.info(f"Loading XTTS-v2 model on {self.device}")
            try:
                self.model = TTS(
                    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                    device=self.device,
                    gpu_memory=self.gpu_memory,
                    compute_type="float32" if self.device == "cpu" else "auto"
                )
                self._model_cache[cache_key] = self.model
            except Exception as e:
                logger.error(f"Failed to load XTTS-v2 model: {e}")
                # Fallback to CPU if GPU fails
                if self.device == "cuda":
                    logger.warning("Falling back to CPU")
                    self.device = "cpu"
                    self.model = TTS(
                        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                        device="cpu",
                        gpu_memory=0
                    )
                else:
                    raise
        
        return self._model_cache[cache_key]
    
    def synthesize(self,
                   text: str,
                   language: str,
                   speaker_reference_path: Optional[str] = None,
                   speaker_name: str = "default") -> np.ndarray:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            language: Language code (e.g., 'ar', 'en', 'hi')
            speaker_reference_path: Path to reference audio for voice cloning
            speaker_name: Name/ID for the speaker
        
        Returns:
            Audio array (mono, 24kHz)
        """
        if not text or not text.strip():
            logger.warning("Empty text for synthesis")
            return np.array([])
        
        logger.info(f"Synthesizing ({language}): {text[:50]}...")
        model = self._get_model()
        
        try:
            if speaker_reference_path and os.path.exists(speaker_reference_path):
                logger.info(f"Using speaker reference: {speaker_reference_path}")
                wav = model.tts(
                    text=text,
                    language=language,
                    speaker_wav=speaker_reference_path,
                    top_p=0.85,
                    temperature=0.75
                )
            else:
                logger.info("Using default speaker")
                wav = model.tts(
                    text=text,
                    language=language,
                    top_p=0.85,
                    temperature=0.75
                )
            
            # Convert to numpy array if needed
            if isinstance(wav, list):
                wav = np.array(wav)
            
            logger.info(f"Synthesis complete: {len(wav)} samples at {model.synthesizer.output_sample_rate}Hz")
            return wav
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            raise
    
    def synthesize_segments(self,
                           segments: List[Dict],
                           language: str,
                           speaker_reference_path: Optional[str] = None) -> List[Dict]:
        """
        Synthesize speech for multiple segments
        
        Args:
            segments: List with 'translated_text', 'start', 'end'
            language: Target language
            speaker_reference_path: Reference audio for voice cloning
        
        Returns:
            Segments with 'audio' arrays added
        """
        logger.info(f"Synthesizing {len(segments)} segments in {language}")
        model = self._get_model()
        
        for i, segment in enumerate(segments):
            try:
                text = segment.get('translated_text', '')
                if not text.strip():
                    segment['audio'] = np.array([])
                    segment['synthesize_status'] = 'skipped'
                    continue
                
                # Synthesize
                if speaker_reference_path and os.path.exists(speaker_reference_path):
                    wav = model.tts(
                        text=text,
                        language=language,
                        speaker_wav=speaker_reference_path
                    )
                else:
                    wav = model.tts(text=text, language=language)
                
                segment['audio'] = np.array(wav) if not isinstance(wav, np.ndarray) else wav
                segment['synthesize_status'] = 'success'
                logger.debug(f"[{i+1}/{len(segments)}] Synthesized {len(segment['audio'])} samples")
                
            except Exception as e:
                logger.error(f"Failed to synthesize segment {i}: {e}")
                segment['audio'] = np.array([])
                segment['synthesize_status'] = 'failed'
                segment['synthesize_error'] = str(e)
        
        return segments
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def validate_language(self, language: str) -> bool:
        """Check if language is supported"""
        return language in self.SUPPORTED_LANGUAGES
