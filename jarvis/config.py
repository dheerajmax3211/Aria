from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Identity
    jarvis_name: str = Field(default="ARIA")
    user_name: str = Field(default="User")
    user_location: str = Field(default="Unknown")
    working_hours_start: int = Field(default=9)
    working_hours_end: int = Field(default=21)

    # Voice
    elevenlabs_api_key: str = Field(default="")
    elevenlabs_voice_id: str = Field(default="")
    wake_word: str = Field(default="hey aria")
    stt_model: str = Field(default="base")
    tts_voice: str = Field(default="en-US-JennyNeural")
    tts_rate: str = Field(default="+15%")
    tts_pitch: str = Field(default="+2Hz")

    # LLM
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="deepseek-r1:8b")
    claude_api_key: str = Field(default="")
    gemini_api_key: str = Field(default="")
    fast_cloud_model: str = Field(default="gemini-2.5-flash")
    reasoning_model: str = Field(default="gemini-2.5-pro")
    llm_mode: str = Field(default="local")

    # Architect (OpenRouter)
    openrouter_api_key: str = Field(default="")
    architect_model: str = Field(default="qwen/qwen3.6-plus:free")

    # Integrations (future phases)
    openweather_api_key: str = Field(default="")
    github_token: str = Field(default="")
    github_username: str = Field(default="")
    telegram_bot_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")
    google_credentials_path: str = Field(default="./integrations/google/credentials.json")

    # Paths
    projects_root: str = Field(default="")
    downloads_folder: str = Field(default="")

    # Scheduling
    morning_briefing_time: str = Field(default="08:00")
    evening_summary_time: str = Field(default="21:00")

    @property
    def elevenlabs_configured(self) -> bool:
        return bool(self.elevenlabs_api_key and self.elevenlabs_voice_id)

    @property
    def claude_configured(self) -> bool:
        return bool(self.claude_api_key)


settings = Settings()
