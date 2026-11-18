from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_", extra="ignore")

    environment: str = "development"
    api_token: str = "dev-atlas-token"
    database_url: str = "sqlite:///./atlas.db"
    artifact_dir: str = "./data/artifacts"
    cors_origins: str = "*"

    openai_api_key: str | None = None
    openai_model: str = "gpt-6-luna"
    openai_base_url: str = "https://api.openai.com/v1"

    def allowed_origins(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
