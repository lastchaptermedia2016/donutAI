"""Tests for voice services (TTS, STT, and fallback manager)."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.groq_api_key = "test_groq_key"
    settings.elevenlabs_api_key = "test_elevenlabs_key"
    settings.xai_api_key = "test_xai_key"
    settings.openai_api_key = "test_openai_key"
    settings.tts_provider = "groq"
    settings.tts_provider_priority = "groq,elevenlabs,xai,browser"
    settings.stt_provider_priority = "groq,elevenlabs,xai,browser"
    settings.xai_model = "grok-2-mini"
    return settings


@pytest.fixture
def mock_groq_client():
    """Mock Groq client for testing."""
    client = AsyncMock()
    client.audio.transcriptions.create.return_value = MagicMock(text="Hello world")
    return client


class TestVoiceFallbackManager:
    """Tests for VoiceFallbackManager."""

    @pytest.mark.asyncio
    async def test_synthesize_with_fallback_success(self, mock_settings):
        """Test successful TTS synthesis with first provider."""
        with patch("backend.app.services.voice_fallback.get_settings", return_value=mock_settings):
            with patch("backend.app.services.tts_service.TTSService") as mock_tts:
                mock_instance = AsyncMock()
                mock_instance.synthesize.return_value = b"audio_data"
                mock_tts.return_value = mock_instance

                from backend.app.services.voice_fallback import VoiceFallbackManager
                manager = VoiceFallbackManager()
                
                audio, provider = await manager.synthesize_with_fallback(
                    text="Hello",
                    voice="alloy",
                    speed=1.0,
                )

                assert audio == b"audio_data"
                assert provider == "groq"

    @pytest.mark.asyncio
    async def test_synthesize_with_fallback_fallback_to_browser(self, mock_settings):
        """Test TTS fallback to browser when all providers fail."""
        with patch("backend.app.services.voice_fallback.get_settings", return_value=mock_settings):
            with patch("backend.app.services.tts_service.TTSService") as mock_tts:
                mock_instance = AsyncMock()
                mock_instance.synthesize.return_value = None
                mock_tts.return_value = mock_instance

                from backend.app.services.voice_fallback import VoiceFallbackManager
                manager = VoiceFallbackManager()
                
                audio, provider = await manager.synthesize_with_fallback(
                    text="Hello",
                    voice="alloy",
                    speed=1.0,
                )

                assert audio is None
                assert provider == "browser"

    @pytest.mark.asyncio
    async def test_transcribe_with_fallback_success(self, mock_settings):
        """Test successful STT transcription with first provider."""
        with patch("backend.app.services.voice_fallback.get_settings", return_value=mock_settings):
            with patch("backend.app.services.stt_service.STTService") as mock_stt:
                mock_instance = AsyncMock()
                mock_instance.transcribe.return_value = "Hello world"
                mock_stt.return_value = mock_instance

                from backend.app.services.voice_fallback import VoiceFallbackManager
                manager = VoiceFallbackManager()
                
                text, provider = await manager.transcribe_with_fallback(
                    audio_data=b"audio_data",
                    language="en",
                )

                assert text == "Hello world"
                assert provider == "groq"

    @pytest.mark.asyncio
    async def test_transcribe_with_fallback_fallback_to_browser(self, mock_settings):
        """Test STT fallback to browser when all providers fail."""
        with patch("backend.app.services.voice_fallback.get_settings", return_value=mock_settings):
            with patch("backend.app.services.stt_service.STTService") as mock_stt:
                mock_instance = AsyncMock()
                mock_instance.transcribe.return_value = None
                mock_stt.return_value = mock_instance

                from backend.app.services.voice_fallback import VoiceFallbackManager
                manager = VoiceFallbackManager()
                
                text, provider = await manager.transcribe_with_fallback(
                    audio_data=b"audio_data",
                    language="en",
                )

                assert text is None
                assert provider == "browser"


class TestTTSService:
    """Tests for TTSService."""

    @pytest.mark.asyncio
    async def test_groq_speak_returns_none(self, mock_settings):
        """Test Groq TTS returns None (uses browser fallback)."""
        with patch("backend.app.services.tts_service.get_settings", return_value=mock_settings):
            from backend.app.services.tts_service import TTSService
            service = TTSService(provider="groq")
            
            audio = await service.synthesize(
                text="Hello",
                voice="alloy",
                speed=1.0,
            )

            # Groq doesn't have native TTS, so it should return None
            assert audio is None

    @pytest.mark.asyncio
    async def test_unknown_provider_returns_none(self, mock_settings):
        """Test unknown provider returns None."""
        with patch("backend.app.services.tts_service.get_settings", return_value=mock_settings):
            from backend.app.services.tts_service import TTSService
            service = TTSService(provider="unknown_provider")
            
            audio = await service.synthesize(
                text="Hello",
                voice="alloy",
                speed=1.0,
            )

            assert audio is None


class TestSTTService:
    """Tests for STTService."""

    @pytest.mark.asyncio
    async def test_groq_transcribe_success(self, mock_settings, mock_groq_client):
        """Test successful Groq STT transcription."""
        with patch("backend.app.services.stt_service.get_settings", return_value=mock_settings):
            with patch("backend.app.services.stt_service.AsyncGroq", return_value=mock_groq_client):
                from backend.app.services.stt_service import STTService
                service = STTService(provider="groq")
                
                text = await service.transcribe(
                    audio_data=b"audio_data",
                    language="en",
                )

                assert text == "Hello world"

    @pytest.mark.asyncio
    async def test_groq_transcribe_failure(self, mock_settings):
        """Test Groq STT transcription failure."""
        with patch("backend.app.services.stt_service.get_settings", return_value=mock_settings):
            with patch("backend.app.services.stt_service.AsyncGroq") as mock_groq:
                mock_client = AsyncMock()
                mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
                mock_groq.return_value = mock_client

                from backend.app.services.stt_service import STTService
                service = STTService(provider="groq")
                
                text = await service.transcribe(
                    audio_data=b"audio_data",
                    language="en",
                )

                assert text is None

    @pytest.mark.asyncio
    async def test_browser_provider_returns_none(self, mock_settings):
        """Test browser provider returns None (frontend handles)."""
        with patch("backend.app.services.stt_service.get_settings", return_value=mock_settings):
            from backend.app.services.stt_service import STTService
            service = STTService(provider="webspeech")
            
            text = await service.transcribe(
                audio_data=b"audio_data",
                language="en",
            )

            # Browser provider returns None so frontend uses Web Speech API
            assert text is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])