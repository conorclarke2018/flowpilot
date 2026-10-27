from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://flowpilot:flowpilot@localhost:5433/flowpilot"
    redis_url: str = "redis://localhost:6379/0"
    environment: str = "development"
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    ai_provider: str = "mock"  # "mock" | "openai"
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_base_url: str | None = None


settings = Settings()
