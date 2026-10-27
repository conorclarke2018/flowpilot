# Architecture Decision Records

Short records of the decisions that shaped FlowPilot's engineering, written as
they were made (or, where noted, reconstructed from the actual build) — context,
the decision, alternatives considered, and consequences. These are the answers
to "why did you build it this way?"

| ADR | Decision |
|-----|----------|
| [001](001-modular-monolith.md) | Modular monolith, not microservices |
| [002](002-versioned-workflow-definitions.md) | Versioned, immutable JSON workflow definitions |
| [003](003-dag-execution.md) | DAG execution with deterministic topological scheduling |
| [004](004-ai-provider-abstraction.md) | Provider-agnostic AI interface with mandatory schema validation |
| [005](005-background-execution-idempotency.md) | Async execution via Celery, with idempotent run creation |
| [006](006-human-approval-safe-resumption.md) | Human approval gates with safe, non-destructive resumption |
| [007](007-local-first-deployment.md) | Local-first deployment with portable infrastructure |
