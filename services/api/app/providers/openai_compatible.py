import json
from typing import Any

from openai import APIError, AsyncOpenAI

from app.providers.base import GenerationError


class OpenAICompatibleProvider:
    """Works against any OpenAI-compatible chat completions endpoint.

    Set `base_url` to target a local/self-hosted model (e.g. Ollama, vLLM)
    instead of the public OpenAI API.
    """

    def __init__(self, *, api_key: str, model: str, base_url: str | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def generate(
        self,
        prompt: str,
        *,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        messages = [{"role": "user", "content": prompt}]
        response_format: dict[str, Any] = {"type": "json_object"} if output_schema else None  # type: ignore[assignment]

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                response_format=response_format,
            )
        except APIError as exc:
            raise GenerationError(str(exc)) from exc

        content = response.choices[0].message.content
        if content is None:
            raise GenerationError("Model returned an empty response")

        if output_schema is None:
            return {"text": content}

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise GenerationError(f"Model response was not valid JSON: {exc}") from exc
