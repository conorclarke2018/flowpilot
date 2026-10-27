import asyncio
from collections.abc import Callable
from typing import Any

import jsonschema

from app.engine.context import ExecutionContext
from app.providers.base import GenerationError
from app.providers.factory import get_provider

NodeHandler = Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]


def handle_trigger_manual(config: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
    return dict(context.trigger_input)


def handle_trigger_webhook(config: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
    return dict(context.trigger_input)


def handle_data_transform(config: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
    mapping: dict[str, Any] = config.get("mapping", {})
    return {key: context.resolve(value) for key, value in mapping.items()}


def handle_action_mock_email(config: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
    resolved_config = context.resolve(config)
    return {
        "sent": True,
        "to": resolved_config.get("to"),
        "subject": resolved_config.get("subject"),
        "body": resolved_config.get("body"),
    }


def handle_ai_classify(config: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
    resolved_config = context.resolve(config)
    prompt = resolved_config.get("prompt", "")
    output_schema = config.get("output_schema")

    provider = get_provider()
    # Node handlers run inside a synchronous executor (invoked from a Celery
    # worker process with no running event loop), so bridge to the async
    # provider interface here rather than making the whole executor async.
    try:
        result = asyncio.run(provider.generate(prompt, output_schema=output_schema))
    except GenerationError as exc:
        raise RuntimeError(f"AI generation failed: {exc}") from exc

    if output_schema is not None:
        try:
            jsonschema.validate(result, output_schema)
        except jsonschema.ValidationError as exc:
            raise RuntimeError(f"AI output failed schema validation: {exc.message}") from exc

    return result


HANDLERS: dict[str, NodeHandler] = {
    "trigger.manual": handle_trigger_manual,
    "trigger.webhook": handle_trigger_webhook,
    "data.transform": handle_data_transform,
    "action.mock_email": handle_action_mock_email,
    "ai.classify": handle_ai_classify,
}
