"""
Voice Clone Service - Speaker voice enhancement and cloning
Uses audio processing to match cloned voice to original speaker characteristics
"""

import logging
import os
from typing import Optional, Dict
import numpy as np
import soundfile as sf
from scipy import signal
import librosa

logger = logging.getLogger(__name__)


class VoiceCloneService:
    """Handles voice cloning and speaker enhancement"""
    
    def __init__(self):
        """Initialize Voice Clone Service"""
        self.sr = 24000  # Standard sample rate
    
    def extract_speaker_characteristics(self, audio_path: str, duration_s: float = 10.0) -> Dict:
        """
        Extract speaker characteristics from reference audio
        
        Args:
            audio_path: Path to reference audio
            duration_s: Duration to analyze (seconds)
        
        Returns:
            Speaker characteristics dict
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")
        
        logger.info(f"Extracting speaker characteristics: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr, duration=duration_s)
            
            # Calculate characteristics
            characteristics = {
                'mean_energy': float(np.mean(np.abs(y))),
                'energy_std': float(np.std(np.abs(y))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'mfcc_mean': np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1).tolist(),
                'sample_rate': sr
            }
            
            logger.info(f"Extracted characteristics: energy={characteristics['mean_energy']:.4f}, "
                       f"pitch={characteristics['spectral_centroid']:.1f}Hz")
            return characteristics
            
        except Exception as e:
            logger.error(f"Failed to extract characteristics: {e}")
            raise
    
    def normalize_audio(self, audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target loudness (EBU R128 standard)
        
        Args:
            audio: Audio array
            target_db: Target loudness in dB
        
        Returns:
            Normalized audio
        """
        if len(audio) == 0:
            return audio
        
        try:
            # Calculate current loudness
            rms = np.sqrt(np.mean(audio ** 2))
            current_db = 20 * np.log10(rms) if rms > 0 else -np.inf
            
            # Calculate gain
            gain_db = target_db - current_db
            gain = 10 ** (gain_db / 20)
            
            # Apply gain with limiting
            normalized = audio * gain
            normalized = np.clip(normalized, -1.0, 1.0)
            
            logger.debug(f"Normalized audio: {current_db:.1f}dB → {target_db:.1f}dB (gain: {gain_db:+.1f}dB)")
            return normalized
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return audio
    
    def reduce_noise(self, audio: np.ndarray, noise_duration_s: float = 1.0) -> np.ndarray:
        """
        Reduce background noise from audio
        
        Args:
            audio: Audio array
            noise_duration_s: Duration of noise profile to use
        
        Returns:
            Denoised audio
        """
        if len(audio) == 0:
            return audio
        
        try:
            from noisereduce import reduce_noise
            
            logger.info("Reducing background noise...")
            
            # Assume first part is noise
            noise_sample_count = int(noise_duration_s * self.sr)
            noise_profile = audio[:min(noise_sample_count, len(audio))]
            
            # Reduce noise
            reduced = reduce_noise(y=audio, sr=self.sr, y_noise=noise_profile)
            
            logger.info("Noise reduction complete")
            return reduced
            
        except ImportError:
            logger.warning("noisereduce not installed, skipping noise reduction")
            return audio
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            return audio
    
    def apply_voice_characteristics(self, audio: np.ndarray,
                                   source_characteristics: Dict,
                                   target_characteristics: Dict) -> np.ndarray:
        """
        Apply source speaker characteristics to synthesized audio
        
        Args:
            audio: Synthesized audio
            source_characteristics: Original speaker characteristics
            target_characteristics: Target characteristics
        
        Returns:
            Enhanced audio
        """
        if len(audio) == 0:
            return audio
        
        try:
            logger.info("Applying speaker characteristics...")
            
            # Normalize to source energy
            source_energy = source_characteristics.get('mean_energy', 0.1)
            target_energy = target_characteristics.get('mean_energy', 0.1)
            
            if target_energy > 0:
                energy_ratio = source_energy / target_energy
                audio = audio * energy_ratio
            
            # Clip to prevent distortion
            audio = np.clip(audio, -1.0, 1.0)
            
            logger.debug(f"Applied characteristics: energy ratio={energy_ratio:.2f}")
            return audio
            
        except Exception as e:
            logger.error(f"Failed to apply characteristics: {e}")
            return audio
    
    def clone_voice(self, synthesized_audio: np.ndarray,
                   reference_audio_path: str) -> np.ndarray:
        """
        Clone voice by matching synthesized audio to reference speaker
        
        Args:
            synthesized_audio: TTS-generated audio
            reference_audio_path: Original speaker audio
        
        Returns:
            Voice-cloned audio
        """
        if len(synthesized_audio) == 0:
            return synthesized_audio
        
        logger.info(f"Voice cloning: synthesized ({len(synthesized_audio)} samples) ← {reference_audio_path}")
        
        try:
            # Extract reference characteristics
            ref_chars = self.extract_speaker_characteristics(reference_audio_path)
            
            # Normalize synthesized audio
            cloned = self.normalize_audio(synthesized_audio, target_db=-20.0)
            
            # Try noise reduction on synthesized
            try:
                cloned = self.reduce_noise(cloned)
            except:
                pass  # Optional step
            
            # Apply reference characteristics
            cloned = self.apply_voice_characteristics(
                cloned,
                source_characteristics=ref_chars,
                target_characteristics={'mean_energy': np.mean(np.abs(cloned))}
            )
            
            logger.info("Voice cloning complete")
            return cloned
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            # Return normalized audio if cloning fails
            return self.normalize_audio(synthesized_audio)
    
    def save_audio(self, audio: np.ndarray, output_path: str, sr: int = 24000) -> str:
        """Save audio to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sf.write(output_path, audio, sr)
        logger.info(f"Saved audio: {output_path}")
        return output_path
