# ADR-004: Provider-agnostic AI interface with mandatory schema validation

## Status

Accepted

## Context

The `ai.classify` node and AI-assisted workflow generation both need an LLM.
The product should never require a paid API key to run locally or in CI, and
the model backing it (mock, a local model, or a hosted provider) shouldn't
change how any calling code is written.

## Decision

Define one `Protocol` (`app/providers/base.py`):

```python
class ModelProvider(Protocol):
    async def generate(self, prompt: str, *, output_schema: dict | None = None) -> dict: ...
```

Three implementations behind a factory (`app/providers/factory.py`,
selected by `settings.ai_provider`, default `"mock"`):

- `MockProvider` — synthesizes a schema-valid response with no network call at
  all (first enum value, placeholder strings, etc.). This is the default, which
  means `pnpm dev`, the test suite, and CI never need an API key.
- `OpenAICompatibleProvider` — works against the real OpenAI API *or* any
  OpenAI-compatible local endpoint (Ollama, vLLM) by setting `base_url`, so
  "local inference" and "hosted inference" are the same code path with a
  different URL, not two providers.

Every call site that needs structured output passes a JSON Schema and
validates the result with `jsonschema` before trusting it — in
`app/nodes/handlers.py::handle_ai_classify` and
`app/services/generation.py::generate_workflow_proposal`. A model returning
malformed or off-schema JSON is treated as a failed node (classify) or a
failed generation attempt eligible for one bounded retry (generate), never as
silently-accepted garbage propagating downstream.

## Alternatives considered

- **Call the OpenAI SDK directly from node handlers**: rejected — it would
  make every node handler untestable without a real or mocked API, and would
  hard-couple the product to one vendor. The actual implementation cost of the
  `Protocol` + factory was about 70 lines total; the payoff was that
  `test_ai_classify.py` and `test_generation.py` never touch the network.
- **Trust model output without schema validation**: rejected outright — this
  is the specific failure mode the spec calls out ("invalid model output is
  handled as an error"), and it's the difference between a toy LLM wrapper and
  something that can safely sit upstream of an action node with real side
  effects.

## Consequences

- Node handlers run inside a **synchronous** executor (ADR-003), but
  `ModelProvider.generate` is `async` — `handle_ai_classify` bridges this with
  `asyncio.run(...)`, documented inline as relying on the executor always
  running in a process with no existing event loop (true for both the Celery
  worker and the test suite). This would break if the executor were ever
  called from inside an async FastAPI request handler directly — a known
  constraint, not a hidden landmine.
- `MockProvider`'s schema-synthesis is deliberately dumb (empty arrays, first
  enum value) — good enough to prove the pipeline wiring is correct, but it
  means the *default* dev experience for AI generation produces an
  intentionally-invalid empty workflow (no trigger node) until a real provider
  is configured. This is visible and logged, not a silent trap — see
  `test_generate_with_mock_provider_is_deterministic_and_reports_invalid`.
