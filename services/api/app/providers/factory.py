from app.core.config import settings
from app.providers.base import ModelProvider
from app.providers.mock import MockProvider
from app.providers.openai_compatible import OpenAICompatibleProvider

_mock_provider = MockProvider()


def get_provider() -> ModelProvider:
    if settings.ai_provider == "mock":
        return _mock_provider

    if settings.ai_provider == "openai":
        return OpenAICompatibleProvider(
            api_key=settings.ai_api_key,
            model=settings.ai_model,
            base_url=settings.ai_base_url,
        )

    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
