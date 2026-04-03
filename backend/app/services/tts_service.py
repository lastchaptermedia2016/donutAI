"""Text-to-Speech service for AI receptionist.

Supports multiple TTS providers with fallback:
- Groq (primary, fast inference)
- ElevenLabs (premium, high quality)
- xAI/Grok (alternative cloud provider)
- OpenAI TTS (cloud, high quality)
- Coqui TTS (local, free)
- Browser SpeechSynthesis (frontend fallback)
"""

import asyncio
import base64
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service with multiple provider support.

    The provider is selected from settings. When no external TTS is
    configured, the system returns plain text that the frontend can
    speak using the browser SpeechSynthesis API.
    """

    def __init__(self, provider: str = "groq"):
        self._provider = provider
        self._initialised = False
        self._engine = None
        self._engine_type = None

    async def _initialize(self) -> bool:
        """Initialize the TTS engine based on provider."""
        if self._initialised:
            return True

        if self._provider == "groq":
            try:
                from groq import AsyncGroq
                from ..config import get_settings
                settings = get_settings()
                if not settings.groq_api_key:
                    logger.warning("Groq API key not configured")
                    return False
                self._engine = AsyncGroq(api_key=settings.groq_api_key)
                self._engine_type = "groq"
                self._initialised = True
                logger.info("Groq TTS engine initialized")
                return True
            except ImportError:
                logger.error("groq not installed - cannot use Groq TTS")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize Groq TTS: {e}")
                return False

        elif self._provider == "elevenlabs":
            try:
                import httpx
                from ..config import get_settings
                settings = get_settings()
                if not settings.elevenlabs_api_key:
                    logger.warning("ElevenLabs API key not configured")
                    return False
                self._engine = httpx.AsyncClient(
                    base_url="https://api.elevenlabs.io/v1",
                    headers={
                        "xi-api-key": settings.elevenlabs_api_key,
                        "Content-Type": "application/json",
                    },
                )
                self._engine_type = "elevenlabs"
                self._initialised = True
                logger.info("ElevenLabs TTS engine initialized")
                return True
            except ImportError:
                logger.error("httpx not installed - cannot use ElevenLabs")
                return False

        elif self._provider == "xai":
            try:
                import httpx
                from ..config import get_settings
                settings = get_settings()
                if not settings.xai_api_key:
                    logger.warning("xAI API key not configured")
                    return False
                self._engine = httpx.AsyncClient(
                    base_url="https://api.x.ai/v1",
                    headers={
                        "Authorization": f"Bearer {settings.xai_api_key}",
                        "Content-Type": "application/json",
                    },
                )
                self._engine_type = "xai"
                self._initialised = True
                logger.info("xAI/Grok TTS engine initialized")
                return True
            except ImportError:
                logger.error("httpx not installed - cannot use xAI")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize xAI TTS: {e}")
                return False

        elif self._provider == "openai":
            try:
                import openai
                from ..config import get_settings
                settings = get_settings()
                if not settings.openai_api_key:
                    logger.warning("OpenAI API key not configured")
                    return False
                self._engine = openai.AsyncOpenAI(api_key=settings.openai_api_key)
                self._engine_type = "openai"
                self._initialised = True
                logger.info("OpenAI TTS engine initialized")
                return True
            except ImportError:
                logger.error("openai not installed - cannot use OpenAI TTS")
                return False

        elif self._provider == "coqui":
            try:
                from TTS.api import TTS
                self._engine = TTS("tts_models/en/ljspeech/tacotron2-DDC")
                self._engine_type = "coqui"
                self._initialised = True
                logger.info("Coqui TTS engine initialized")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Coqui TTS: {e}")
                return False

        else:
            logger.info(f"Unknown TTS provider '{self._provider}', falling back to text-only")
            self._initialised = True
            return True

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> Optional[bytes]:
        """Synthesize speech from text.

        Returns:
            Audio bytes (wav format) or None if provider unavailable.
            When provider is not configured, returns None so frontend can
            use browser SpeechSynthesis as fallback.
        """
        if not text:
            return None

        if not await self._initialize():
            logger.warning("TTS engine not available, returning text for browser TTS")
            return None

        try:
            if self._engine_type == "groq":
                return await self._groq_speak(text, voice, speed)
            elif self._engine_type == "elevenlabs":
                return await self._elevenlabs_speak(text, voice, speed)
            elif self._engine_type == "xai":
                return await self._xai_speak(text, voice, speed)
            elif self._engine_type == "openai":
                return await self._openai_speak(text, voice, speed)
            elif self._engine_type == "coqui":
                return self._coqui_speak(text, speed)
            else:
                return None
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None

    async def _groq_speak(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Optional[bytes]:
        """Synthesize using Groq API."""
        if isinstance(self._engine, type(None)):
            return None

        try:
            response = await self._engine.audio.speech.create(
                model="canopylabs/orpheus-v1-english",
                input=text[:4096],
                voice=voice or "autumn",
                response_format="wav",
                speed=speed,
            )
            return response.read()
        except Exception as e:
            logger.error(f"Groq TTS error: {e}")
            # Fallback to browser if Groq TTS fails
            return None

    async def _elevenlabs_speak(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Optional[bytes]:
        """Synthesize using ElevenLabs."""
        voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # Default voice
        if isinstance(self._engine, type(None)):
            return None

        response = await self._engine.post(
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
            return response.content
        logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
        return None

    async def _xai_speak(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Optional[bytes]:
        """Synthesize using xAI/Grok API."""
        if isinstance(self._engine, type(None)):
            return None

        try:
            from ..config import get_settings
            settings = get_settings()
            
            # xAI/Grok TTS endpoint
            response = await self._engine.post(
                "/audio/speech",
                json={
                    "model": settings.xai_model,
                    "input": text[:4096],
                    "voice": voice or "alloy",
                    "response_format": "wav",
                    "speed": speed,
                },
            )
            if response.status_code == 200:
                return response.content
            logger.error(f"xAI API error: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"xAI TTS error: {e}")
            return None

    async def _openai_speak(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Optional[bytes]:
        """Synthesize using OpenAI TTS."""
        voice_name = voice or "alloy"
        response = await self._engine.audio.speech.create(
            model="tts-1",
            voice=voice_name,
            input=text[:4096],  # OpenAI TTS limit
            response_format="wav",
            speed=speed,
        )
        return response.read()

    def _coqui_speak(self, text: str, speed: float = 1.0) -> Optional[bytes]:
        """Synthesize using Coqui TTS (local)."""
        if self._engine is None:
            return None

        output_buffer = io.BytesIO()
        self._engine.tts_to_file(
            text,
            file_path=output_buffer,
            speaker="p363",
        )
        output_buffer.seek(0)
        return output_buffer.read()


_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """Get TTS service singleton."""
    global _service
    if _service is None:
        try:
            from ..config import get_settings
            settings = get_settings()
            _service = TTSService(provider=settings.tts_provider)
        except Exception:
            _service = TTSService(provider="groq")
    return _service