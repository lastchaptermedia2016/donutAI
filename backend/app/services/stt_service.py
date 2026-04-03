"""Speech-to-Text service for AI receptionist.

Supports multiple STT providers with fallback:
- Groq (primary, fast inference using Whisper)
- ElevenLabs (premium, high accuracy)
- xAI/Grok (alternative cloud provider)
- OpenAI Whisper (cloud, high quality)
- whisper.cpp (local, free, requires binary)
- Web Speech API (browser, frontend fallback)

When no STT provider is configured, the frontend uses the browser
Web Speech API directly. The backend STT endpoint accepts audio
and returns transcription.
"""

import asyncio
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service with multiple provider support.

    The frontend uses Web Speech API (browser built-in) by default.
    When higher accuracy is needed, the backend STT endpoint can use
    various cloud providers or local whisper.cpp.
    """

    def __init__(self, provider: str = "groq"):
        self._provider = provider
        self._initialised = False
        self._engine = None
        self._engine_type = None

    async def _initialize(self) -> bool:
        """Initialize the STT engine based on provider."""
        if self._initialised:
            return True

        if self._provider == "groq":
            try:
                from groq import AsyncGroq
                from ..config import get_settings

                settings = get_settings()
                if not settings.groq_api_key:
                    logger.warning("Groq API key not configured for STT")
                    return False
                self._engine = AsyncGroq(api_key=settings.groq_api_key)
                self._engine_type = "groq"
                self._initialised = True
                logger.info("Groq STT engine initialized")
                return True
            except ImportError:
                logger.error("groq not installed - cannot use Groq STT")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize Groq STT: {e}")
                return False

        elif self._provider == "elevenlabs":
            try:
                import httpx
                from ..config import get_settings

                settings = get_settings()
                if not settings.elevenlabs_api_key:
                    logger.warning("ElevenLabs API key not configured for STT")
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
                logger.info("ElevenLabs STT engine initialized")
                return True
            except ImportError:
                logger.error("httpx not installed - cannot use ElevenLabs STT")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs STT: {e}")
                return False

        elif self._provider == "xai":
            try:
                import httpx
                from ..config import get_settings

                settings = get_settings()
                if not settings.xai_api_key:
                    logger.warning("xAI API key not configured for STT")
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
                logger.info("xAI/Grok STT engine initialized")
                return True
            except ImportError:
                logger.error("httpx not installed - cannot use xAI STT")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize xAI STT: {e}")
                return False

        elif self._provider == "whisper":
            try:
                import openai
                from ..config import get_settings

                settings = get_settings()
                if not settings.openai_api_key:
                    logger.warning("OpenAI API key not configured for Whisper")
                    return False
                self._engine = openai.AsyncOpenAI(api_key=settings.openai_api_key)
                self._engine_type = "whisper"
                self._initialised = True
                logger.info("OpenAI Whisper STT engine initialized")
                return True
            except ImportError:
                logger.error("openai not installed - cannot use Whisper")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize Whisper STT: {e}")
                return False

        elif self._provider == "whisper_cpp":
            # whisper.cpp integration - requires whisper-cpp binary
            try:
                import subprocess
                self._engine = {"available": True}
                self._engine_type = "whisper_cpp"
                self._initialised = True
                logger.info("whisper.cpp STT engine initialized")
                return True
            except Exception as e:
                logger.error(f"whisper.cpp not available: {e}")
                return False

        elif self._provider == "webspeech":
            # Web Speech API - handled entirely in frontend
            self._initialised = True
            self._engine_type = "webspeech"
            logger.info("STT set to Web Speech API (frontend only)")
            return True

        else:
            logger.info(f"Unknown STT provider '{self._provider}', using Web Speech API fallback")
            self._initialised = True
            return True

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> Optional[str]:
        """Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes (wav or ogg format preferred)
            language: Language code for transcription

        Returns:
            Transcribed text or None if transcription failed.
        """
        if not audio_data:
            return None

        if not await self._initialize():
            logger.warning("STT engine not available")
            return None

        try:
            if self._engine_type == "groq":
                return await self._groq_transcribe(audio_data, language)
            elif self._engine_type == "elevenlabs":
                return await self._elevenlabs_transcribe(audio_data, language)
            elif self._engine_type == "xai":
                return await self._xai_transcribe(audio_data, language)
            elif self._engine_type == "whisper":
                return await self._whisper_transcribe(audio_data, language)
            elif self._engine_type == "whisper_cpp":
                return await self._whisper_cpp_transcribe(audio_data, language)
            else:
                logger.info("STT provider not configured - use frontend Web Speech API")
                return None
        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return None

    async def _groq_transcribe(
        self, audio_data: bytes, language: str = "en"
    ) -> Optional[str]:
        """Transcribe using Groq's Whisper API.
        
        Groq provides fast Whisper inference in the cloud.
        """
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        try:
            # Use Groq's Whisper endpoint
            response = await self._engine.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
            )
            return response.text
        except Exception as e:
            logger.error(f"Groq STT error: {e}")
            return None

    async def _elevenlabs_transcribe(
        self, audio_data: bytes, language: str = "en"
    ) -> Optional[str]:
        """Transcribe using ElevenLabs STT."""
        if isinstance(self._engine, type(None)):
            return None

        try:
            files = {"file": ("audio.wav", audio_data, "audio/wav")}
            response = await self._engine.post(
                "/speech-to-text",
                files=files,
                data={"model_id": "scribe_v1", "language_code": language},
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            logger.error(f"ElevenLabs STT error: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"ElevenLabs STT error: {e}")
            return None

    async def _xai_transcribe(
        self, audio_data: bytes, language: str = "en"
    ) -> Optional[str]:
        """Transcribe using xAI/Grok STT."""
        if isinstance(self._engine, type(None)):
            return None

        try:
            from ..config import get_settings
            settings = get_settings()
            
            files = {"file": ("audio.wav", audio_data, "audio/wav")}
            data = {
                "model": settings.xai_model,
                "language": language,
            }
            response = await self._engine.post(
                "/audio/transcriptions",
                files=files,
                data=data,
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            logger.error(f"xAI STT error: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"xAI STT error: {e}")
            return None

    async def _whisper_transcribe(
        self, audio_data: bytes, language: str = "en"
    ) -> Optional[str]:
        """Transcribe using OpenAI Whisper API.

        Expects audio data in wav/ogg/mp3/mp4/mpeg/mpeg4/mpga/m4a format.
        Max file size is 25MB.
        """
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        response = await self._engine.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
        )
        return response.text

    async def _whisper_cpp_transcribe(
        self, audio_data: bytes, language: str = "en"
    ) -> Optional[str]:
        """Transcribe using whisper.cpp (local)."""
        # Save audio to temp file and call whisper-cpp
        import tempfile
        import subprocess
        import os

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            audio_path = f.name

        try:
            result = subprocess.run(
                ["whisper-cpp", "--model", "base", "--file", audio_path, "--language", language],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error("whisper.cpp timed out")
            return None
        except FileNotFoundError:
            logger.error("whisper-cpp binary not found")
            return None
        finally:
            os.unlink(audio_path)


_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    """Get STT service singleton."""
    global _service
    if _service is None:
        try:
            from ..config import get_settings
            settings = get_settings()
            # Parse provider priority list
            providers = settings.stt_provider_priority.split(",")
            primary_provider = providers[0].strip() if providers else "groq"
            _service = STTService(provider=primary_provider)
        except Exception:
            _service = STTService(provider="groq")
    return _service