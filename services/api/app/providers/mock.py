from typing import Any


class MockProvider:
    """Deterministic provider for local development and tests.

    Synthesizes a schema-valid response without calling any real model, so the
    rest of the application never needs network access or API keys to run.
    """

    async def generate(
        self,
        prompt: str,
        *,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if output_schema is None:
            return {"text": f"mock response to: {prompt[:100]}"}
        return _synthesize(output_schema)


def _synthesize(schema: dict[str, Any]) -> Any:
    schema_type = schema.get("type", "object")

    if "enum" in schema:
        return schema["enum"][0]

    if schema_type == "object":
        properties = schema.get("properties", {})
        return {key: _synthesize(subschema) for key, subschema in properties.items()}

    if schema_type == "array":
        return []

    if schema_type == "string":
        return "mock value"

    if schema_type in ("integer", "number"):
        return 0

    if schema_type == "boolean":
        return False

    return None
