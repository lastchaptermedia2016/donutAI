"""Voice Fallback Manager for TTS/STT services.

This module provides a unified interface for TTS and STT with automatic
fallback to alternative providers when the primary provider fails.

Fallback order (configurable via environment):
    TTS: Groq → ElevenLabs → xAI → Browser
    STT: Groq → ElevenLabs → xAI → Browser
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceFallbackManager:
    """Manages TTS/STT provider fallback chain.

    Tries providers in order of priority, falling back to the next
    provider if the current one fails or is unavailable.
    """

    def __init__(self):
        self._tts_providers: list[str] = []
        self._stt_providers: list[str] = []
        self._initialised = False

    async def _initialize(self) -> bool:
        """Initialize provider lists from settings."""
        if self._initialised:
            return True

        try:
            from ..config import get_settings
            settings = get_settings()

            # Parse TTS provider priority
            tts_priority = settings.tts_provider_priority
            self._tts_providers = [p.strip() for p in tts_priority.split(",") if p.strip()]

            # Parse STT provider priority
            stt_priority = settings.stt_provider_priority
            self._stt_providers = [p.strip() for p in stt_priority.split(",") if p.strip()]

            logger.info(f"TTS provider priority: {self._tts_providers}")
            logger.info(f"STT provider priority: {self._stt_providers}")

            self._initialised = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize voice fallback manager: {e}")
            # Use default fallback order
            self._tts_providers = ["groq", "elevenlabs", "xai", "browser"]
            self._stt_providers = ["groq", "elevenlabs", "xai", "browser"]
            self._initialised = True
            return True

    async def synthesize_with_fallback(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> tuple[Optional[bytes], str]:
        """Synthesize speech with automatic provider fallback.

        Args:
            text: Text to synthesize
            voice: Voice identifier (provider-specific)
            speed: Speech speed multiplier

        Returns:
            Tuple of (audio_bytes, provider_name)
            audio_bytes is None if all providers fail (browser should handle TTS)
            provider_name indicates which provider was used or "browser" for fallback
        """
        if not text:
            return None, "none"

        await self._initialize()

        for provider in self._tts_providers:
            if provider == "browser":
                # Browser fallback - return None so frontend uses SpeechSynthesis
                logger.info("TTS: Falling back to browser SpeechSynthesis")
                return None, "browser"

            try:
                from .tts_service import TTSService
                service = TTSService(provider=provider)
                audio = await service.synthesize(text, voice=voice, speed=speed)

                if audio:
                    logger.info(f"TTS: Successfully synthesized using {provider}")
                    return audio, provider
                else:
                    logger.warning(f"TTS: {provider} returned no audio, trying next provider")
            except Exception as e:
                logger.warning(f"TTS: {provider} failed: {e}, trying next provider")
                continue

        # All providers failed - use browser fallback
        logger.warning("TTS: All providers failed, falling back to browser")
        return None, "browser"

    async def transcribe_with_fallback(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> tuple[Optional[str], str]:
        """Transcribe audio with automatic provider fallback.

        Args:
            audio_data: Raw audio bytes
            language: Language code for transcription

        Returns:
            Tuple of (transcribed_text, provider_name)
            transcribed_text is None if all providers fail
            provider_name indicates which provider was used or "browser" for fallback
        """
        if not audio_data:
            return None, "none"

        await self._initialize()

        for provider in self._stt_providers:
            if provider == "browser":
                # Browser fallback - return None so frontend uses Web Speech API
                logger.info("STT: Falling back to browser Web Speech API")
                return None, "browser"

            try:
                from .stt_service import STTService
                service = STTService(provider=provider)
                text = await service.transcribe(audio_data, language=language)

                if text:
                    logger.info(f"STT: Successfully transcribed using {provider}")
                    return text, provider
                else:
                    logger.warning(f"STT: {provider} returned no text, trying next provider")
            except Exception as e:
                logger.warning(f"STT: {provider} failed: {e}, trying next provider")
                continue

        # All providers failed - use browser fallback
        logger.warning("STT: All providers failed, falling back to browser")
        return None, "browser"

    def get_available_providers(self) -> dict:
        """Get lists of configured providers."""
        return {
            "tts": self._tts_providers,
            "stt": self._stt_providers,
        }


# Singleton instance
_manager: Optional[VoiceFallbackManager] = None


def get_voice_fallback_manager() -> VoiceFallbackManager:
    """Get voice fallback manager singleton."""
    global _manager
    if _manager is None:
        _manager = VoiceFallbackManager()
    return _manager