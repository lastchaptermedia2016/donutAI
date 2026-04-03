"""Donut backend configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Groq Configuration (Required)
    groq_api_key: str = Field(..., description="Groq API key for LLM inference")

    # LLM Settings
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Primary LLM model for agent reasoning",
    )
    intent_model: str = Field(
        default="llama-3.1-8b-instant",
        description="Fast model for intent classification",
    )

    # Server Settings
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    frontend_url: str = Field(default="http://localhost:3000")

    # Optional: OpenAI (for Whisper fallback)
    openai_api_key: str | None = Field(default=None)

    # Optional: Google APIs
    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)
    google_redirect_uri: str | None = Field(default=None)

    # JWT Secret
    jwt_secret: str = Field(
        default="change_me_to_random_string",
        description="Secret key for JWT token signing",
    )

    # Auth Passphrase
    admin_passphrase: str = Field(
        default="donut-admin",
        description="Passphrase for admin authentication",
    )

    # TTS/STT Provider Priority (comma-separated fallback order)
    tts_provider_priority: str = Field(
        default="groq,elevenlabs,xai,browser",
        description="Comma-separated list of TTS providers in fallback order",
    )
    stt_provider_priority: str = Field(
        default="groq,elevenlabs,xai,browser",
        description="Comma-separated list of STT providers in fallback order",
    )

    # TTS Settings
    tts_provider: str = Field(
        default="groq",
        description="Primary TTS provider",
    )
    elevenlabs_api_key: str | None = Field(default=None)

    # xAI/Grok Configuration
    xai_api_key: str | None = Field(default=None)
    xai_model: str = Field(default="grok-2-mini")

    # Supabase Configuration
    supabase_url: str = Field(
        default="https://your-project.supabase.co",
        description="Supabase project URL",
    )
    supabase_key: str = Field(
        default="your-anon-key",
        description="Supabase anon/public key",
    )

    # Database paths (deprecated - using Supabase now)
    sqlite_db_path: Path = Field(default=DATA_DIR / "donut.sqlite")
    lancedb_path: Path = Field(default=DATA_DIR / "lancedb")

    # Conversation settings
    max_ring_buffer_size: int = Field(
        default=50,
        description="Maximum messages kept in rolling buffer",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model for embedding memories",
    )

    # Receptionist Settings
    business_name: str = Field(default="Donut Receptionist")
    working_hours_start: int = Field(default=9, description="Start hour (0-23)")
    working_hours_end: int = Field(default=17, description="End hour (0-23)")
    appointment_slot_duration: int = Field(default=30, description="Duration in minutes")

    @property
    def api_base_url(self) -> str:
        """Base URL for the FastAPI server."""
        return f"http://{self.backend_host}:{self.backend_port}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()