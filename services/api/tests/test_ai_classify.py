import pytest

from app.engine.context import ExecutionContext
from app.nodes.handlers import handle_ai_classify
from app.providers.base import GenerationError

CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["delivery", "billing", "other"]},
        "priority": {"type": "string", "enum": ["low", "normal", "high"]},
        "summary": {"type": "string"},
    },
    "required": ["category", "priority", "summary"],
    "additionalProperties": False,
}


def test_ai_classify_returns_schema_valid_output_from_mock_provider() -> None:
    context = ExecutionContext({"message": "My order never arrived"})
    config = {"prompt": "Classify: $.trigger.message", "output_schema": CLASSIFY_SCHEMA}

    result = handle_ai_classify(config, context)

    assert result["category"] == "delivery"  # first enum value, per mock synthesis
    assert set(result.keys()) == {"category", "priority", "summary"}


def test_ai_classify_resolves_prompt_references(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_prompts = []

    class RecordingProvider:
        async def generate(self, prompt, *, output_schema=None):
            captured_prompts.append(prompt)
            return {"category": "other", "priority": "low", "summary": "ok"}

    monkeypatch.setattr(
        "app.nodes.handlers.get_provider", lambda: RecordingProvider()
    )

    context = ExecutionContext({"message": "Where is my refund?"})
    handle_ai_classify(
        {"prompt": "$.trigger.message", "output_schema": CLASSIFY_SCHEMA}, context
    )

    assert captured_prompts == ["Where is my refund?"]


def test_ai_classify_raises_on_schema_violation(monkeypatch: pytest.MonkeyPatch) -> None:
    class BadProvider:
        async def generate(self, prompt, *, output_schema=None):
            return {"category": "not-a-valid-enum-value"}

    monkeypatch.setattr("app.nodes.handlers.get_provider", lambda: BadProvider())

    context = ExecutionContext({})
    with pytest.raises(RuntimeError, match="schema validation"):
        handle_ai_classify({"prompt": "x", "output_schema": CLASSIFY_SCHEMA}, context)


def test_ai_classify_raises_on_provider_generation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingProvider:
        async def generate(self, prompt, *, output_schema=None):
            raise GenerationError("upstream timeout")

    monkeypatch.setattr("app.nodes.handlers.get_provider", lambda: FailingProvider())

    context = ExecutionContext({})
    with pytest.raises(RuntimeError, match="AI generation failed"):
        handle_ai_classify({"prompt": "x", "output_schema": CLASSIFY_SCHEMA}, context)
