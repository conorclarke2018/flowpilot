from typing import Any

from pydantic import ValidationError as PydanticValidationError

from app.engine.registry import NODE_TYPES
from app.engine.validation import WorkflowValidationResult, validate_workflow
from app.providers.base import GenerationError, ModelProvider
from app.schemas.workflow import WorkflowDefinition

MAX_ATTEMPTS = 2

GENERATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": sorted(NODE_TYPES)},
                    "position": {
                        "type": "object",
                        "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
                        "required": ["x", "y"],
                    },
                    "config": {"type": "object"},
                },
                "required": ["id", "type", "position"],
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                },
                "required": ["id", "source", "target"],
            },
        },
    },
    "required": ["name", "nodes", "edges"],
}


def _build_prompt(user_prompt: str, previous_errors: list[str] | None) -> str:
    base = (
        "Design a workflow automation as a JSON object with fields "
        "name, nodes (each with id, type, position, config) and edges "
        "(each with id, source, target). Only use these node types: "
        f"{', '.join(sorted(NODE_TYPES))}. Exactly one node must be a trigger "
        "node (trigger.manual or trigger.webhook).\n\n"
        f"Automation description: {user_prompt}"
    )
    if previous_errors:
        base += (
            "\n\nThe previous attempt failed validation with these errors, fix them: "
            + "; ".join(previous_errors)
        )
    return base


async def generate_workflow_proposal(
    provider: ModelProvider, prompt: str
) -> tuple[WorkflowDefinition, WorkflowValidationResult, int]:
    previous_errors: list[str] | None = None
    definition = WorkflowDefinition(name="Untitled workflow", nodes=[], edges=[])
    result = WorkflowValidationResult([])

    for attempt in range(1, MAX_ATTEMPTS + 1):
        generation_prompt = _build_prompt(prompt, previous_errors)

        try:
            raw = await provider.generate(generation_prompt, output_schema=GENERATION_SCHEMA)
            for node in raw.get("nodes", []):
                node.setdefault("config", {})
            definition = WorkflowDefinition.model_validate(raw)
        except (GenerationError, PydanticValidationError) as exc:
            previous_errors = [str(exc)]
            continue

        result = validate_workflow(definition)
        if result.is_valid:
            return definition, result, attempt

        previous_errors = [f"[{e.code}] {e.message}" for e in result.errors]

    return definition, result, MAX_ATTEMPTS
