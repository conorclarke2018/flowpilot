import pytest

from app.providers.mock import MockProvider
from app.services.generation import MAX_ATTEMPTS, generate_workflow_proposal

VALID_WORKFLOW_RAW = {
    "name": "Triage",
    "nodes": [
        {"id": "trigger_1", "type": "trigger.manual", "position": {"x": 0, "y": 0}, "config": {}},
        {
            "id": "email_1",
            "type": "action.mock_email",
            "position": {"x": 200, "y": 0},
            "config": {"to": "x", "subject": "x", "body": "x"},
        },
    ],
    "edges": [{"id": "edge_1", "source": "trigger_1", "target": "email_1"}],
}


class FixedProvider:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls: list[str] = []

    async def generate(self, prompt, *, output_schema=None):
        self.calls.append(prompt)
        return self.response


@pytest.mark.asyncio
async def test_generate_valid_workflow_succeeds_on_first_attempt() -> None:
    provider = FixedProvider(VALID_WORKFLOW_RAW)

    definition, result, attempts = await generate_workflow_proposal(
        provider, "Triage customer enquiries"
    )

    assert result.is_valid
    assert attempts == 1
    assert len(provider.calls) == 1
    assert definition.name == "Triage"
    assert [n.id for n in definition.nodes] == ["trigger_1", "email_1"]


@pytest.mark.asyncio
async def test_generate_restricted_node_types_in_prompt() -> None:
    provider = FixedProvider(VALID_WORKFLOW_RAW)

    await generate_workflow_proposal(provider, "Do something")

    assert "trigger.manual" in provider.calls[0]
    assert "action.mock_email" in provider.calls[0]


@pytest.mark.asyncio
async def test_generate_retries_once_on_invalid_output_then_gives_up() -> None:
    # No trigger node -> always fails validate_workflow's trigger-count rule.
    invalid_raw = {
        "name": "No trigger",
        "nodes": [
            {
                "id": "email_1",
                "type": "action.mock_email",
                "position": {"x": 0, "y": 0},
                "config": {},
            }
        ],
        "edges": [],
    }
    provider = FixedProvider(invalid_raw)

    definition, result, attempts = await generate_workflow_proposal(provider, "Do something")

    assert not result.is_valid
    assert attempts == MAX_ATTEMPTS
    assert len(provider.calls) == MAX_ATTEMPTS
    # second attempt's prompt should mention the earlier failure
    assert "invalid_trigger_count" in provider.calls[1]
    assert definition.name == "No trigger"


@pytest.mark.asyncio
async def test_generate_with_mock_provider_is_deterministic_and_reports_invalid() -> None:
    provider = MockProvider()

    definition, result, attempts = await generate_workflow_proposal(
        provider, "Triage customer enquiries"
    )

    # the schema-synthesis mock always produces empty nodes/edges arrays,
    # which is a validly-shaped but workflow-invalid (no trigger) proposal
    assert not result.is_valid
    assert attempts == MAX_ATTEMPTS
    assert definition.nodes == []
