"""Voice services for Donut AI.

This module provides:
- STT (Speech-to-Text): Groq Whisper → Browser fallback
- TTS (Text-to-Speech): ElevenLabs (limited) → Browser fallback
- Credit tracking for ElevenLabs free tier (10k chars/month)

$0 Tier Strategy:
- Groq Whisper: Primary STT (fast, accurate)
- ElevenLabs: Premium TTS for briefings only (10k chars/month)
- Browser TTS: Routine conversations (unlimited, free)
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# ============================================
# Credit Tracking
# ============================================

class ElevenLabsCreditTracker:
    """Track ElevenLabs usage to stay within free tier (10k chars/month)."""
    
    def __init__(self):
        self.monthly_limit = 10000
        self.used_this_month = 0
        self.reset_date = self._get_next_reset_date()
    
    def _get_next_reset_date(self) -> datetime:
        """Get the first day of next month."""
        now = datetime.now()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        return datetime(now.year, now.month + 1, 1)
    
    def _check_reset(self):
        """Reset counter if we've crossed into a new month."""
        if datetime.now() >= self.reset_date:
            self.used_this_month = 0
            self.reset_date = self._get_next_reset_date()
            logger.info("ElevenLabs credit tracker reset for new month")
    
    def can_use(self, text_length: int) -> bool:
        """Check if we have enough credits for this text."""
        self._check_reset()
        return (self.used_this_month + text_length) <= self.monthly_limit
    
    def use(self, text_length: int):
        """Record usage of ElevenLabs credits."""
        self._check_reset()
        self.used_this_month += text_length
        logger.info(f"ElevenLabs credits used: {self.used_this_month}/{self.monthly_limit}")
    
    def get_remaining(self) -> int:
        """Get remaining credits for this month."""
        self._check_reset()
        return self.monthly_limit - self.used_this_month
    
    def to_dict(self) -> dict:
        """Export state for persistence."""
        return {
            "used_this_month": self.used_this_month,
            "reset_date": self.reset_date.isoformat(),
        }
    
    def from_dict(self, data: dict):
        """Import state from persistence."""
        self.used_this_month = data.get("used_this_month", 0)
        if "reset_date" in data:
            self.reset_date = datetime.fromisoformat(data["reset_date"])


# Global credit tracker
_credit_tracker = ElevenLabsCreditTracker()


def get_credit_tracker() -> ElevenLabsCreditTracker:
    """Get the ElevenLabs credit tracker."""
    return _credit_tracker


# ============================================
# STT Service (Groq Whisper)
# ============================================

class STTService:
    """Speech-to-Text service using Groq Whisper.
    
    Groq provides fast, accurate Whisper inference for free.
    Falls back to browser STT if Groq is unavailable.
    """
    
    def __init__(self):
        self._client = None
        self._initialized = False
    
    async def _initialize(self) -> bool:
        """Initialize Groq client."""
        if self._initialized:
            return True
        
        try:
            from groq import AsyncGroq
            from ..config import get_settings
            
            settings = get_settings()
            if not settings.groq_api_key:
                logger.warning("Groq API key not configured")
                return False
            
            self._client = AsyncGroq(api_key=settings.groq_api_key)
            self._initialized = True
            logger.info("Groq STT (Whisper) initialized")
            return True
        except ImportError:
            logger.error("groq not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Groq STT: {e}")
            return False
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> Optional[str]:
        """Transcribe audio using Groq Whisper.
        
        Args:
            audio_data: Raw audio bytes (wav/ogg/mp3)
            language: Language code
            
        Returns:
            Transcribed text or None if failed
        """
        if not await self._initialize():
            logger.warning("STT: Falling back to browser")
            return None
        
        try:
            import io
            
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            response = await self._client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
            )
            
            text = response.text
            logger.info(f"STT: Transcribed {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Groq STT error: {e}")
            return None


# ============================================
# TTS Service (ElevenLabs + Browser fallback)
# ============================================

class TTSService:
    """Text-to-Speech service with ElevenLabs and browser fallback.
    
    Strategy:
    - ElevenLabs: Premium voice for high-impact moments (briefings)
    - Browser TTS: Routine conversations (free, unlimited)
    
    Credit Management:
    - Tracks ElevenLabs usage (10k chars/month free tier)
    - Falls back to browser when credits are low
    """
    
    def __init__(self):
        self._client = None
        self._initialized = False
    
    async def _initialize(self) -> bool:
        """Initialize ElevenLabs client."""
        if self._initialized:
            return True
        
        try:
            import httpx
            from ..config import get_settings
            
            settings = get_settings()
            if not settings.elevenlabs_api_key:
                logger.warning("ElevenLabs API key not configured")
                return False
            
            self._client = httpx.AsyncClient(
                base_url="https://api.elevenlabs.io/v1",
                headers={
                    "xi-api-key": settings.elevenlabs_api_key,
                    "Content-Type": "application/json",
                },
            )
            self._initialized = True
            logger.info("ElevenLabs TTS initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs: {e}")
            return False
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        use_premium: bool = False,
    ) -> Optional[bytes]:
        """Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice ID (ElevenLabs)
            speed: Speech speed multiplier
            use_premium: If True, use ElevenLabs (limited credits)
                        If False, return None for browser TTS
        
        Returns:
            Audio bytes (wav) or None for browser fallback
        """
        if not text:
            return None
        
        # Check if we should use premium TTS
        if not use_premium:
            logger.info("TTS: Using browser TTS (routine mode)")
            return None
        
        # Check credits
        if not _credit_tracker.can_use(len(text)):
            logger.warning(f"TTS: ElevenLabs credits low ({_credit_tracker.get_remaining()} remaining)")
            return None
        
        # Initialize if needed
        if not await self._initialize():
            logger.warning("TTS: ElevenLabs unavailable, using browser")
            return None
        
        try:
            voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # Default voice
            
            response = await self._client.post(
                f"/text-to-speech/{voice_id}",
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5,
                    },
                },
            )
            
            if response.status_code == 200:
                _credit_tracker.use(len(text))
                logger.info(f"TTS: Synthesized {len(text)} chars (ElevenLabs)")
                return response.content
            else:
                logger.error(f"ElevenLabs API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return None
    
    def should_use_premium(self, context: str = "routine") -> bool:
        """Determine if we should use premium TTS.
        
        Args:
            context: "briefing" for premium, "routine" for browser
        
        Returns:
            True if premium TTS should be used
        """
        if context == "briefing":
            # Use premium for morning briefings, important announcements
            return _credit_tracker.get_remaining() > 500  # Keep buffer
        return False


# ============================================
# Service Singletons
# ============================================

_stt_service: Optional[STTService] = None
_tts_service: Optional[TTSService] = None


def get_stt_service() -> STTService:
    """Get STT service singleton."""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service


def get_tts_service() -> TTSService:
    """Get TTS service singleton."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


# ============================================
# Convenience Functions
# ============================================

async def transcribe_audio(audio_data: bytes, language: str = "en") -> Optional[str]:
    """Convenience function for STT."""
    service = get_stt_service()
    return await service.transcribe(audio_data, language)


async def synthesize_speech(
    text: str,
    voice: Optional[str] = None,
    use_premium: bool = False,
) -> Optional[bytes]:
    """Convenience function for TTS."""
    service = get_tts_service()
    return await service.synthesize(text, voice, use_premium=use_premium)


def get_voice_status() -> dict:
    """Get current voice service status."""
    return {
        "stt_provider": "groq_whisper",
        "tts_provider": "elevenlabs" if _tts_service and _tts_service._initialized else "browser",
        "elevenlabs_credits_remaining": _credit_tracker.get_remaining(),
        "elevenlabs_credits_limit": _credit_tracker.monthly_limit,
    }