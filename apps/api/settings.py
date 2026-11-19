from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_", extra="ignore")

    environment: str = "development"
    api_token: str = "dev-atlas-token"
    owner_code: str = "000000"
    session_secret: str = "dev-session-secret-change-me"
    session_days: int = 30
    database_url: str = "sqlite:///./atlas.db"
    artifact_dir: str = "./data/artifacts"
    cors_origins: str = "*"
    publication_email: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True

    openai_api_key: str | None = None
    openai_model: str = "gpt-6-luna"
    openai_realtime_model: str = "gpt-realtime-2.1-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    anthropic_api_key: str | None = None
    anthropic_model: str = ""
    anthropic_base_url: str = "https://api.anthropic.com/v1"

    ollama_url: str | None = None
    ollama_model: str = "llama3.2"

    kimi_api_key: str | None = None
    kimi_base_url: str = "https://api.moonshot.ai/v1"
    kimi_model: str = ""
    qwen_api_key: str | None = None
    qwen_base_url: str = ""
    qwen_model: str = ""

    def allowed_origins(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
