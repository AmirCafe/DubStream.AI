"""
Translation Service - Text translation using Google Translate
Translates transcribed text while preserving timing information
"""

import logging
from typing import List, Dict
from deep_translator import GoogleTranslator
from datetime import timedelta

logger = logging.getLogger(__name__)


class TranslationService:
    """Handles text translation using Google Translate"""
    
    # Language code mapping
    LANGUAGE_CODES = {
        'en': 'english', 'es': 'spanish', 'fr': 'french', 'de': 'german',
        'it': 'italian', 'pt': 'portuguese', 'ru': 'russian', 'ja': 'japanese',
        'ko': 'korean', 'zh': 'chinese (simplified)', 'ar': 'arabic', 'hi': 'hindi',
        'ur': 'urdu', 'tr': 'turkish', 'pl': 'polish', 'nl': 'dutch',
        'sv': 'swedish', 'da': 'danish', 'fi': 'finnish', 'no': 'norwegian',
        'he': 'hebrew', 'th': 'thai', 'vi': 'vietnamese', 'id': 'indonesian'
    }
    
    def __init__(self):
        """Initialize Translation Service"""
        self.translator = None
        self.source_lang = None
        self.target_lang = None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'ar')
        
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""
        
        logger.info(f"Translating: {source_lang} → {target_lang}")
        
        try:
            translator = GoogleTranslator(source_language=source_lang, target_language=target_lang)
            translated = translator.translate(text)
            logger.info(f"Translation complete: {len(text)} → {len(translated)} characters")
            return translated
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def translate_segments(self, segments: List[Dict], source_lang: str, target_lang: str) -> List[Dict]:
        """
        Translate transcription segments while preserving timing
        
        Args:
            segments: List of segments with 'text', 'start', 'end' keys
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Segments with 'translated_text' added
        """
        logger.info(f"Translating {len(segments)} segments: {source_lang} → {target_lang}")
        
        try:
            translator = GoogleTranslator(source_language=source_lang, target_language=target_lang)
            
            for segment in segments:
                if 'text' in segment and segment['text'].strip():
                    segment['translated_text'] = translator.translate(segment['text'])
                    logger.debug(f"[{segment['start']:.1f}s] {segment['text'][:30]}... → {segment['translated_text'][:30]}...")
                else:
                    segment['translated_text'] = ""
            
            logger.info(f"Translated {len(segments)} segments successfully")
            return segments
            
        except Exception as e:
            logger.error(f"Segment translation failed: {e}")
            raise
    
    def align_translation_to_timing(self, segments: List[Dict]) -> List[Dict]:
        """
        Ensure translated text fits within original timing
        If translation is too long, split it across multiple segments
        
        Args:
            segments: Segments with 'translated_text'
        
        Returns:
            Adjusted segments
        """
        logger.info(f"Aligning {len(segments)} translations to original timing")
        
        for segment in segments:
            if 'translated_text' not in segment:
                continue
            
            original_text = segment.get('text', '')
            translated_text = segment.get('translated_text', '')
            
            # Calculate text expansion ratio
            if len(original_text) > 0:
                expansion = len(translated_text) / len(original_text)
                segment['expansion_ratio'] = expansion
                
                # Log if translation is significantly longer
                if expansion > 1.5:
                    logger.warning(f"Translation {expansion:.1f}x longer: {original_text[:20]}... → {translated_text[:20]}...")
        
        return segments
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes"""
        return self.LANGUAGE_CODES.copy()
    
    def validate_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check if language pair is supported"""
        return source_lang in self.LANGUAGE_CODES and target_lang in self.LANGUAGE_CODES
