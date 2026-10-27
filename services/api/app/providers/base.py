from typing import Any, Protocol


class GenerationError(Exception):
    pass


class ModelProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        *,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a JSON-serializable object. Raises GenerationError on failure."""
        ...
