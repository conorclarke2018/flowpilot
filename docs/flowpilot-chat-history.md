# FlowPilot --- Conversation History

> Export of the FlowPilot planning conversation in this chat. Assistant
> replies are transcribed in Markdown. Inline image-search previews from
> the chat UI are represented by brief notes rather than embedded image
> files.

------------------------------------------------------------------------

## User

sass app

## Assistant

Are you looking to build a **SaaS app**, or do you mean something else
by "sass app"?

If you mean a SaaS application, I can help you plan and build one using
your preferred stack:

-   **Frontend:** TypeScript, React and Next.js
-   **Backend:** Python with FastAPI
-   **Database:** PostgreSQL
-   **Infrastructure:** Terraform and Docker
-   **AI:** An LLM that can run locally during development and be hosted
    in the cloud for production

Are you looking for **SaaS app ideas**, a full application architecture,
or help building a specific app? I can also create an image of the
proposed architecture.

## User

yes, I need a project which I can use for my resume

## Assistant

For your CV, I'd recommend building a **proper AI SaaS product that
solves a real business problem**, rather than another chatbot, to-do
list or basic CRUD application.

Given your experience with TypeScript, Next.js, Python, FastAPI, Docker
and Terraform, the project should demonstrate that you can build and
deploy a complete product, integrate AI into a useful workflow, and make
sensible engineering decisions.

The goal is to have something you can discuss in software engineering
and AI interviews, demonstrate on GitHub, and show to potential
employers when applying for AI engineer, software engineer or
forward-deployed engineer roles.

### My top project recommendation

> Image preview in the original chat: AI workflow automation dashboard
> with connected nodes.

### 1. FlowPilot --- AI Workflow Automation SaaS

A platform that lets small businesses automate repetitive tasks using
configurable workflows, AI models and integrations.

**Example:** A business receives customer support emails. The system
classifies each email, extracts key details, drafts a response and sends
it for human approval before taking action.

### 2. DevFlow AI --- Developer Productivity Platform

Connect a Git repository to summarise pull requests, explain code
changes, identify potential bugs and generate release notes.

**Why it stands out:** Directly relevant to software engineering roles,
with opportunities to demonstrate Git integrations, asynchronous jobs,
code analysis and AI evaluation.

### 3. KnowledgeBase AI --- Business Knowledge Assistant

Teams upload documents and search them through an AI assistant that
provides cited answers, permissions-aware retrieval and document
management.

**Why it stands out:** Demonstrates retrieval-augmented generation
(RAG), embeddings, vector search, document processing and access
control.

I would choose **FlowPilot**, because it combines AI engineering,
full-stack development, infrastructure and a product you could
eventually turn into a real business.

### What you would build

> Image preview in the original chat: dark-mode workflow automation
> dashboard with a visual node editor.

The core product would have four main areas:

-   **Workflow builder:** Create workflows by connecting trigger,
    processing, AI and action nodes.
-   **AI engine:** Configure prompts, select models and process
    structured outputs.
-   **Integrations:** Start with webhooks and email, then add services
    such as Slack or GitHub.
-   **Execution dashboard:** View run history, errors, costs, latency
    and individual workflow steps.

### Recommended technical architecture

-   **Next.js + TypeScript:** Dashboard, workflow editor and
    authentication.
-   **FastAPI:** REST API, validation and workflow orchestration.
-   **PostgreSQL:** Users, workflows and executions.
-   **Redis + worker:** Background executions and retries.
-   **LLM adapter:** Local models or hosted APIs.
-   **Docker:** Reproducible environments.
-   **Terraform + cloud infrastructure:** Deployment, configuration,
    scaling and monitoring.

This stack gives you a credible opportunity to demonstrate
production-minded engineering rather than just connecting a frontend to
an LLM API.

### A realistic 6-week development plan

**Week 1 --- Product foundation** - Define user stories and database
schema. - Set up Next.js, FastAPI, PostgreSQL and Docker Compose. -
Implement authentication and initial API tests.

**Week 2 --- Workflow engine** - Design a JSON workflow definition. -
Implement triggers, conditional steps and sequential execution. - Add
input validation and execution logs.

**Week 3 --- AI integration** - Build a provider abstraction supporting
a local model and hosted LLM. - Add structured outputs, prompt templates
and error handling. - Create an email classification and drafting
workflow.

**Week 4 --- User interface** - Build a visual workflow editor. - Add
execution history, workflow editing and manual approval. - Show errors
and individual step outputs.

**Week 5 --- Testing and deployment** - Add pytest and Playwright
tests. - Build CI/CD for Docker images. - Provision a test environment
using Terraform.

**Week 6 --- Portfolio polish** - Add monitoring, rate limits and
security controls. - Record a demo and write architecture
documentation. - Publish a polished README with screenshots and setup
instructions.

### What will make it stand out on your CV?

  -----------------------------------------------------------------------
  Area                                Evidence to demonstrate
  ----------------------------------- -----------------------------------
  AI engineering                      Model abstraction, structured
                                      output validation, evaluation
                                      dataset and fallback handling

  Backend engineering                 Async tasks, retries, API
                                      validation, database migrations and
                                      integration tests

  Frontend engineering                Interactive workflow editor,
                                      execution visualisation and useful
                                      error states

  DevOps                              Docker, CI/CD, Terraform,
                                      deployment and monitoring

  Security                            Tenant isolation, secret
                                      management, rate limits and
                                      approval before consequential
                                      actions

  Product thinking                    A defined target audience, a useful
                                      workflow and feedback from real
                                      test users
  -----------------------------------------------------------------------

For AI workflows, I would particularly implement **human approval gates,
execution tracing and measurable evaluation**. These make the
application more credible than a simple wrapper around an LLM.

### Example CV entry

Once you have implemented and verified the relevant features, your CV
entry could look like this:

> **FlowPilot --- AI Workflow Automation SaaS** \| TypeScript, Next.js,
> Python, FastAPI, PostgreSQL, Docker, Terraform
>
> -   Developed a full-stack AI workflow automation platform enabling
>     users to configure, execute and monitor multi-step workflows.
> -   Built an asynchronous Python execution engine with structured LLM
>     outputs, retry handling and execution-level observability.
> -   Implemented a provider-agnostic AI architecture supporting local
>     inference and hosted model APIs.
> -   Automated container builds, testing and infrastructure deployment
>     using CI/CD and Terraform.
> -   Evaluated workflow reliability using automated tests and a
>     repeatable dataset of representative AI tasks.

These are example CV bullets for the intended project, not claims to use
before the features are built. Add measured results when you have them.

### Initial choices

The conversation then selected FlowPilot and moved into a more detailed
product specification.

------------------------------------------------------------------------

## User

flowpiolt let build this out further

## Assistant

Let's turn **FlowPilot** into a proper product specification before we
start coding. The aim is to build something that could genuinely be used
by a small business, while giving you strong evidence of AI engineering,
full-stack development, cloud infrastructure and software design for
your CV.

I'd build it as a modular AI automation platform, with a clear first use
case rather than trying to compete with every automation tool at once.

# FlowPilot --- product concept

> Image preview in the original chat: premium dark navy workflow
> automation SaaS interface with a visual node editor.

**Tagline:** Automate the repetitive. Keep humans in control.

FlowPilot lets users build workflows that combine conventional logic, AI
processing and external integrations. Users can see exactly what
happened at each step, inspect failures and require approval before
sensitive actions execute.

The key distinction is that this isn't just an AI chatbot. It's an
**execution engine with a visual interface**, where AI is one component
of a workflow rather than the entire product.

## 1. Who are we building it for?

I'd initially target small businesses and technical teams that
repeatedly process information across emails, documents and business
systems.

### Customer support teams

Classify incoming messages, extract order or customer details, draft
responses and route complicated cases to a person.

### Operations teams

Turn forms and documents into structured records, flag missing
information and notify the right person.

### Technical teams

Automate webhook processing, issue triage, release-note generation and
routine developer workflows.

My recommendation is to use **customer support email processing as the
first demonstration workflow**, while designing the platform so that
other use cases can be added without rewriting the engine.

## 2. The core user experience

FlowPilot should have six main areas.

### Dashboard

Overview of active workflows, total executions, success rates, recent
failures and estimated AI usage costs.

### Workflow builder

A drag-and-drop canvas with triggers, actions, AI nodes, conditional
branches and approval steps. Users configure each node in a side panel.

### Test and run

Run a workflow with sample input, inspect outputs at each step and
validate the workflow before activating it.

### Execution history

A searchable list of executions, including their status, duration,
failed step, model usage and retry history.

### Approval inbox

Users review AI-generated drafts or proposed actions, then approve, edit
or reject them before execution continues.

### Integrations and settings

Configure model providers, API credentials, webhook endpoints, workspace
members and usage limits.

## 3. The first workflow we should actually build

Rather than beginning with a huge library of integrations, make one
complete workflow excellent.

1.  **Webhook trigger:** Receive a customer enquiry.
2.  **Validate input:** Check required fields and reject invalid
    payloads.
3.  **AI classification:** Return category, urgency and a structured
    summary.
4.  **Conditional branch:** Route by urgency or category.
5.  **Human approval:** Review and edit the proposed response.
6.  **Action:** Send to a test endpoint or email integration.

A user should be able to create this workflow, test it with sample
customer messages and follow its execution from start to finish.

For the first version, the final action should use a mock email sender
or test endpoint. Real customer emails can come later, once
authentication, secret management, retries and approval handling are
reliable.

## 4. What belongs in the MVP?

The MVP should include:

-   User accounts and workspaces.
-   Create, edit and save workflows.
-   Visual node editor.
-   Webhook and manual triggers.
-   AI node with structured output.
-   Conditions and variable mapping.
-   Sequential/background execution.
-   Retries, timeouts and failure states.
-   Execution logs and step outputs.
-   Human approval step.
-   Local and hosted model providers.
-   Docker Compose development setup.
-   Automated tests and CI/CD.

Save for later: subscriptions and billing, marketplace, team analytics,
dozens of integrations, autonomous agents and sophisticated multi-region
deployment. These are not necessary to prove the core product works.

## 5. Technical architecture

I would keep the system modular from the beginning, but avoid
microservices. A modular FastAPI application with a separate background
worker is enough for the initial scale.

-   **Next.js web application:** TypeScript, React, React Flow, Tailwind
    CSS.
-   **FastAPI API:** Authentication, validation, workflow CRUD and
    trigger management.
-   **PostgreSQL:** Workflows, users, runs and audit records.
-   **Redis + worker:** Queued jobs, retries and asynchronous execution.
-   **Workflow execution engine:** Node registry, execution context,
    conditions, error handling and approval pauses.
-   **Local inference:** Ollama or another compatible endpoint.
-   **Hosted inference:** Cloud model APIs.

### How the execution engine should work

This is the most technically important part of FlowPilot.

Store workflows as versioned JSON definitions.

``` json
{
  "name": "Customer Enquiry Triage",
  "nodes": [
    {
      "id": "trigger",
      "type": "webhook",
      "config": {}
    },
    {
      "id": "classify",
      "type": "ai.classify",
      "config": {
        "model": "default",
        "output_schema": {
          "category": "string",
          "priority": "string",
          "summary": "string"
        }
      }
    },
    {
      "id": "route",
      "type": "condition",
      "config": {
        "field": "classify.priority",
        "operator": "equals",
        "value": "high"
      }
    }
  ],
  "edges": [
    { "source": "trigger", "target": "classify" },
    { "source": "classify", "target": "route" }
  ]
}
```

This is an illustrative definition, not yet a complete executable
schema. You would define the permitted node types, configuration
schemas, connections and validation rules explicitly.

The engine would:

1.  Validate the workflow graph and its configuration.
2.  Create an execution record with a unique ID and workflow version.
3.  Schedule runnable nodes in dependency order.
4.  Resolve input variables and execute each node through a registered
    handler.
5.  Persist outputs, status, timing and errors for each step.
6.  Pause when approval is required, then resume after a decision.
7.  Mark the run as completed, failed or cancelled.

Use **Pydantic models** to validate node configurations, and keep each
node's execution logic separate from the API routes.

For reliability, add execution timeouts, idempotency keys for external
actions, bounded retries and concurrency limits. Do not simply rerun an
entire workflow after a partial failure: an earlier email or external
action might already have succeeded.

## 6. Supporting local and cloud AI

One of your best differentiators would be making the AI provider
interchangeable.

Define a common interface in Python, such as:

``` python
from typing import Any, Protocol


class ModelProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        *,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...
```

Then implement separate adapters for:

-   **Local models:** a locally hosted model endpoint for development,
    experimentation and privacy-conscious deployments.
-   **Hosted models:** a provider API for stronger models or production
    workloads.
-   **Mock provider:** deterministic responses for unit tests, so tests
    don't need a running LLM or incur API costs.

The interface is only a starting point; production adapters will also
need timeouts, structured-output validation, usage tracking and
provider-specific error handling.

The frontend should never need to know which model vendor is being used.
Provider credentials belong on the backend, and the selected provider
should be configured per environment or workspace with appropriate
access controls.

## 7. Database design

Start with a relational model. PostgreSQL is well suited to the
ownership relationships and execution records, while JSONB can store
flexible workflow definitions and node outputs.

  Table                 Purpose
  --------------------- ----------------------------------------------------
  `users`               User accounts and identity references
  `workspaces`          Workspace and tenant boundaries
  `workspace_members`   Membership and roles
  `workflows`           Workflow metadata and ownership
  `workflow_versions`   Immutable published workflow definitions
  `workflow_runs`       Status, trigger input, timing and overall result
  `node_runs`           Individual node status, outputs, timing and errors
  `approvals`           Pending decisions, reviewer and decision history
  `integrations`        Connection metadata and credential references
  `audit_events`        Important user actions and security events

A key design decision: **separate editable workflows from published
versions**. Editing a workflow should not change a run that's already
executing. Each run references the exact published version it started
with.

Use SQLAlchemy or SQLModel with Alembic migrations. Enforce
workspace-level access in backend queries, and don't store raw API
secrets in ordinary workflow JSON.

## 8. Repository structure

I'd use a monorepo so the frontend, backend and infrastructure can
evolve together.

``` text
flowpilot/
├── apps/
│   └── web/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   │   ├── workflow-editor/
│       │   │   ├── dashboard/
│       │   │   └── execution-viewer/
│       │   ├── features/
│       │   └── lib/
│       └── package.json
├── services/
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── engine/
│       │   │   ├── executor.py
│       │   │   ├── registry.py
│       │   │   └── context.py
│       │   ├── nodes/
│       │   ├── providers/
│       │   └── workers/
│       ├── migrations/
│       └── tests/
├── infra/
│   └── terraform/
├── docker-compose.yml
├── .github/                 # Or your chosen CI provider
├── pnpm-workspace.yaml
├── .env.example
├── .gitignore
└── README.md
```

Keep the workflow engine independent of FastAPI where practical. This
makes it easier to test the engine directly and potentially expose it
through a different API or run it in a separate worker process later.

## 9. Deployment and infrastructure

Start locally with Docker Compose, then deploy a small cloud environment
using Terraform once the core application works.

### Development

Next.js, FastAPI, PostgreSQL, Redis, worker and optional local model
endpoint.

### CI/CD

Lint, type-check, test, build container images, scan dependencies and
publish versioned images to a registry.

### Cloud deployment

Terraform provisions networking, application hosting, managed
PostgreSQL, secrets and monitoring. AWS is a sensible option for your
portfolio.

Don't expose Redis or PostgreSQL publicly. Protect webhook endpoints
against abuse, encrypt credentials, redact secrets from logs and treat
workflow input as untrusted data. AI-generated content should never be
allowed to execute arbitrary Python or shell commands.

## 10. How to make this a genuinely strong portfolio project

Beyond a working demo, aim to produce five pieces of evidence:

-   A live demo or short recorded walkthrough.
-   A clean Git repository with useful commits, tests and a CI pipeline.
-   An architecture diagram and short architecture decision records
    explaining important trade-offs.
-   An evaluation report comparing AI classification accuracy,
    schema-valid output rate, latency and cost across representative
    test cases.
-   A deployment guide explaining how to run it locally and provision
    the cloud version.

You can then show employers not just that you built an AI application,
but that you understand reliability, deployment, testing, security and
measurable AI quality.

------------------------------------------------------------------------

## User

Finalise FlowPilot's product specification and initial implementation
plan. Workflow creation: both. Initial audience: small-business.
Deployment target: local-first. Keep Next.js/TypeScript, FastAPI/Python,
PostgreSQL, Docker and Terraform where appropriate. Specify the MVP
requirements, user journeys, API contracts, workflow JSON schema,
repository setup and the exact first development tasks.

## Assistant

# FlowPilot --- final product specification

*Product blueprint · MVP v1.0 · Local-first architecture*

FlowPilot will be an AI-powered workflow automation SaaS for small
businesses. Users will be able to build automations visually or describe
them in natural language and have AI generate a workflow they can
inspect, edit, test and publish.

The core engineering principle is that **AI proposes workflows, but a
deterministic execution engine validates and runs them**. The LLM will
not execute arbitrary code or decide which security controls to bypass.

> Image preview in the original chat: premium dark navy workflow
> automation dashboard with visual node editor.

## 1. Product definition

**Problem:** Small businesses repeatedly process customer enquiries,
copy information between tools and perform routine administrative tasks
manually.

**Solution:** A visual automation platform that combines triggers,
ordinary logic, AI-powered data processing and actions in reusable
workflows.

**Initial customer:** A small business with a small operations or
customer support team that wants to automate repetitive tasks without
building its own software.

**Differentiator:** AI-assisted workflow creation, transparent
step-by-step execution, local model support and human approval before
consequential actions.

### The first use case

Build a customer enquiry triage workflow:

1.  Receive an enquiry through a webhook or sample input.
2.  Validate the input.
3.  Classify the enquiry using an AI model.
4.  Route it based on category or urgency.
5.  Draft a response and pause for human approval.
6.  Send the approved result to a mock email integration or test
    endpoint.
7.  Record the outcome, timing, errors and model usage.

This single workflow should demonstrate the complete product lifecycle,
from creation through to monitored execution.

## 2. Final technology decisions

  -----------------------------------------------------------------------
  Component               Decision                Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                Next.js, TypeScript     Application UI and
                                                  dashboard

  Workflow editor         React Flow              Visual node graph
                          (`@xyflow/react`)       

  Styling                 Tailwind CSS            Consistent UI
                                                  components

  Backend                 Python, FastAPI         REST API and business
                                                  logic

  Validation              Pydantic                API contracts and node
                                                  configuration

  Database                PostgreSQL              Users, workflows and
                                                  execution records

  ORM and migrations      SQLAlchemy 2 + Alembic  Persistence and schema
                                                  changes

  Background jobs         Redis + Celery          Async workflow
                                                  execution and retries

  AI abstraction          Provider interface +    Local, hosted and mock
                          adapters                models

  Testing                 pytest + Vitest +       Unit, integration and
                          Playwright              end-to-end tests

  Containers              Docker Compose          Reproducible local
                                                  environment

  Infrastructure          Terraform               Future reproducible
                                                  cloud deployment

  CI/CD                   GitHub Actions or       Lint, test, build and
                          GitLab CI               deploy
  -----------------------------------------------------------------------

**Architecture decision:** start with a modular monolith plus a separate
background worker, not a fleet of microservices. The API and worker can
share application modules and database models while running as separate
containers.

For local development, the app should work without cloud infrastructure.
A mock AI provider should make the test suite independent of model
availability; local inference can be added using an OpenAI-compatible
endpoint or another provider adapter. Terraform comes after the local
MVP is working.

## 3. MVP requirements and acceptance criteria

### P0 --- Workflow management

-   Create, edit, save, duplicate and publish workflows.
-   Keep draft definitions separate from immutable published versions.
-   Validate node configurations and graph connections before
    publishing.

**Acceptance:** invalid workflows cannot be published; published
versions remain unchanged when a draft is edited.

### P0 --- Visual and AI-assisted creation

-   Drag nodes onto a canvas and connect their inputs and outputs.
-   Describe an automation in natural language.
-   Preview the AI-generated graph and edit it before publishing.

**Acceptance:** generated workflows pass the same validation as manually
created workflows. Generation never automatically publishes or executes
them.

### P0 --- Execution engine

-   Support webhook/manual triggers, AI processing, variable mapping and
    conditional branches.
-   Persist run status and per-node input/output metadata.
-   Handle timeouts, bounded retries, failures and cancellation.

**Acceptance:** an execution can be inspected after completion, and a
failed run does not silently repeat already completed external actions.

### P0 --- AI and human review

-   Support a mock provider and one real local or hosted provider.
-   Validate structured AI outputs against declared schemas.
-   Pause a workflow for approval and resume it after a decision.

**Acceptance:** invalid model output is handled as an error, and a
pending approval cannot trigger the protected action.

### P1 --- Production-readiness improvements

-   Workspace invitations and granular roles.
-   Encrypted integration secrets and secret rotation.
-   Usage budgets, cost reporting, metrics and alerts.
-   Additional integrations and scheduled triggers.

Implement these after the core end-to-end workflow works reliably.

For the first version, authentication and workspace isolation should
still be present before exposing the app to external users. You can
defer invitations, sophisticated role management and commercial billing.

## 4. User journeys

### Journey A --- create a workflow visually

1.  **Create workflow:** Enter a name and start with a blank canvas or
    template.
2.  **Add nodes:** Choose a trigger, AI classification, condition,
    approval and action.
3.  **Configure and connect:** Set node options and map outputs into
    downstream inputs.
4.  **Validate and test:** Check graph structure and run against sample
    input.
5.  **Publish:** Create an immutable version of the validated workflow.
6.  **Run and inspect:** Execute a run and inspect each node's status,
    output and duration.

### Journey B --- generate a workflow with AI

1.  The user enters: "Classify incoming customer enquiries, flag urgent
    messages and prepare a response for review."
2.  The backend sends the request to the selected model provider with a
    restricted workflow-generation schema.
3.  The model returns a proposed graph using only supported node types.
4.  The backend validates node configuration, edges, references and
    graph constraints.
5.  The UI displays the graph and any validation issues.
6.  The user edits and tests it, then explicitly publishes it.

The model should generate **workflow definitions, not executable Python
or JavaScript**. If generation fails validation, return actionable
errors and allow a bounded regeneration attempt.

### Journey C --- approve an AI-generated action

1.  An execution reaches an approval node.
2.  The run becomes `waiting_for_approval`; the worker releases the task
    rather than blocking a process indefinitely.
3.  An authorised user reviews the proposed response.
4.  The user approves, edits and approves, or rejects it.
5.  The backend records the decision and resumes the run from the
    approval boundary.
6.  The downstream action executes once, subject to idempotency and
    action-specific safety checks.

Approval records should be associated with a specific run, node and
proposed payload. A changed payload must require a new approval.

## 5. API contracts

Use a versioned REST API under `/api/v1`. Keep the browser-facing API
independent of the underlying AI provider and execution queue.

  -----------------------------------------------------------------------------------
  Method                  Endpoint                            Purpose
  ----------------------- ----------------------------------- -----------------------
  `GET`                   `/api/v1/health`                    Application health

  `POST`                  `/api/v1/workflows`                 Create a workflow

  `GET`                   `/api/v1/workflows`                 List accessible
                                                              workflows

  `GET`                   `/api/v1/workflows/{id}`            Get workflow and
                                                              current draft

  `PUT`                   `/api/v1/workflows/{id}`            Update draft definition

  `POST`                  `/api/v1/workflows/{id}/validate`   Validate a graph

  `POST`                  `/api/v1/workflows/{id}/generate`   Generate a proposed
                                                              workflow

  `POST`                  `/api/v1/workflows/{id}/publish`    Publish a new version

  `POST`                  `/api/v1/workflows/{id}/runs`       Start an execution

  `GET`                   `/api/v1/runs/{id}`                 Get execution status

  `GET`                   `/api/v1/runs/{id}/nodes`           Inspect node executions

  `POST`                  `/api/v1/runs/{id}/cancel`          Request cancellation

  `GET`                   `/api/v1/approvals`                 List pending approvals

  `POST`                  `/api/v1/approvals/{id}/decision`   Approve or reject

  `POST`                  `/api/v1/webhooks/{workflow_id}`    Receive external
                                                              trigger
  -----------------------------------------------------------------------------------

For the webhook endpoint, verify that the workflow is published and
enabled, validate the request, apply rate limits and authenticate
callers using a configured signing secret or token. Do not expose
internal workflow IDs as sufficient authentication.

### Example: create a workflow

`POST /api/v1/workflows`

Request:

``` json
{
  "name": "Customer Enquiry Triage",
  "description": "Classify and draft replies for customer enquiries",
  "definition": {
    "schema_version": "1.0",
    "nodes": [],
    "edges": []
  }
}
```

Response: `201 Created`

``` json
{
  "id": "wf_123",
  "name": "Customer Enquiry Triage",
  "status": "draft",
  "draft_revision": 1,
  "published_version": null
}
```

The example IDs are illustrative. In the implementation, use UUIDs or
another well-defined identifier strategy.

### Example: start an execution

`POST /api/v1/workflows/{id}/runs`

Request:

``` json
{
  "input": {
    "customer_email": "customer@example.test",
    "subject": "Order delivery problem",
    "message": "My order has not arrived."
  }
}
```

Response: `202 Accepted`

``` json
{
  "run_id": "run_456",
  "status": "queued",
  "workflow_version": 1,
  "created_at": "2026-10-27T09:00:00Z"
}
```

Execution should be asynchronous. The API creates the run and queues it;
the worker processes it independently.

Use consistent error responses with a machine-readable code, a
human-readable message and optional field-level validation errors.
Return `404` for inaccessible resources where appropriate to avoid
disclosing another workspace's data.

### Execution status model

-   `queued`
-   `running`
-   `waiting_for_approval`
-   `succeeded`
-   `failed`
-   `cancelled`

The state machine should enforce valid transitions, including resuming
an approved run without re-executing earlier successful nodes.
Cancellation and failure handling must account for actions already in
progress.

## 6. Workflow JSON schema

This is the central contract shared by the frontend, API, AI generator
and execution engine. Define it once conceptually and enforce it through
Pydantic on the backend, with matching TypeScript types on the frontend.

### Canonical workflow definition

``` json
{
  "schema_version": "1.0",
  "name": "Customer Enquiry Triage",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger.webhook",
      "position": { "x": 80, "y": 160 },
      "config": {}
    },
    {
      "id": "classify_1",
      "type": "ai.classify",
      "position": { "x": 360, "y": 160 },
      "config": {
        "provider": "default",
        "prompt": "Classify this customer enquiry.",
        "output_schema": {
          "type": "object",
          "properties": {
            "category": {
              "type": "string",
              "enum": ["delivery", "billing", "product", "other"]
            },
            "priority": {
              "type": "string",
              "enum": ["low", "normal", "high"]
            },
            "summary": { "type": "string" }
          },
          "required": ["category", "priority", "summary"],
          "additionalProperties": false
        }
      }
    },
    {
      "id": "approval_1",
      "type": "human.approval",
      "position": { "x": 640, "y": 160 },
      "config": {
        "title": "Review proposed response"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "trigger_1",
      "source_handle": "output",
      "target": "classify_1",
      "target_handle": "input"
    },
    {
      "id": "edge_2",
      "source": "classify_1",
      "source_handle": "output",
      "target": "approval_1",
      "target_handle": "input"
    }
  ]
}
```

This is an illustrative definition; the first schema implementation must
formalise its validation rules and supported node configurations.

### Node registry

  -----------------------------------------------------------------------
  Node type               Responsibility          MVP
  ----------------------- ----------------------- -----------------------
  `trigger.manual`        Run with supplied input Yes

  `trigger.webhook`       Accept external input   Yes

  `data.transform`        Map or reshape JSON     Yes
                          data                    

  `ai.classify`           Produce validated       Yes
                          structured output       

  `logic.condition`       Select a branch using   Yes
                          deterministic rules     

  `human.approval`        Pause until an          Yes
                          authorised decision     

  `action.mock_email`     Record a simulated      Yes
                          email action            

  `action.webhook`        Send data to a          Later, or limited MVP
                          configured endpoint     
  -----------------------------------------------------------------------

The registry should define each node's configuration schema,
input/output contracts, execution handler, timeout and whether it has
external side effects.

For the MVP, start with a **directed acyclic graph (DAG)**. Support
branching, but not loops or arbitrary cycles. DAGs are easier to
validate, schedule and debug.

### Rules the backend must enforce

-   Every node and edge has a unique ID within the workflow.
-   Every edge references existing nodes and valid handles.
-   The graph contains no cycles.
-   Exactly one entry trigger is defined for each published executable
    workflow.
-   Required node configuration is valid for the declared node type.
-   Data references only refer to available upstream outputs.
-   Untrusted model output cannot introduce executable code or
    unsupported node types.
-   Published versions are immutable and each execution references a
    specific version.
-   Secrets are referenced indirectly; they are never embedded in a
    published workflow definition.

For branching, the condition node can expose named outputs such as
`true` and `false`. The scheduler follows only the selected outgoing
branch.

## 7. Repository setup

I recommend `pnpm` for the frontend and a `uv`-managed Python project
for the backend. Keep the frontend and backend independently
installable, with Docker Compose orchestrating local services.

``` text
flowpilot/
├── apps/
│   └── web/
│       ├── src/app/
│       ├── src/components/
│       ├── src/features/workflows/
│       ├── src/features/runs/
│       ├── src/lib/api/
│       ├── src/types/
│       └── package.json
├── services/
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── api/v1/
│       │   ├── core/
│       │   ├── db/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── engine/
│       │   ├── nodes/
│       │   ├── providers/
│       │   └── workers/
│       ├── migrations/
│       ├── tests/
│       ├── pyproject.toml
│       └── Dockerfile
├── packages/
│   └── workflow-contracts/
│       └── README.md
├── infra/
│   └── terraform/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── decisions/
├── docker-compose.yml
├── pnpm-workspace.yaml
├── .env.example
├── .gitignore
└── README.md
```

`packages/workflow-contracts` initially documents the canonical schema
and its versioning rules. Don't maintain two independently evolving
definitions: generate TypeScript types from a formal JSON Schema or
OpenAPI contract where practical.

### Local development services

Your first Compose setup should contain:

-   `web` --- Next.js development server.
-   `api` --- FastAPI with reload enabled.
-   `worker` --- background task process.
-   `postgres` --- persistent database volume.
-   `redis` --- queue broker.
-   Optional local model service --- started only when needed.

The mock model provider should work without the optional model service.
This keeps initial development fast and tests deterministic.

Use `.env.example` to document configuration variables, but keep real
`.env` files out of version control. Pin dependency versions, use health
checks and wait for dependencies to become ready rather than relying
only on container startup order.

### Local-first deployment strategy

**Phase 1: Local development** --- Everything runs on your machine
through Docker Compose, with mock AI and optional local inference.

**Phase 2: Self-hosted demo** --- Deploy the same containers to a Linux
server or VM. Use persistent storage, TLS and protected secrets.

**Phase 3: Terraform-managed cloud** --- Add an AWS deployment with
managed database services, networking, secrets and monitoring, without
changing workflow definitions.

Terraform belongs in the repository from the beginning, but you don't
need to provision cloud resources until the application works locally.
Initially, document the target deployment architecture and leave the
cloud module for a later milestone.

## 8. Exact first development tasks

Start with a small, testable vertical slice rather than building the
entire UI before the backend exists.

### Phase 1 --- Foundation

1.  **Create the monorepo:** Initialise Git, pnpm workspace, Next.js app
    and uv-managed FastAPI project.
2.  **Set up code quality:** Configure TypeScript strict mode, ESLint,
    Prettier, Ruff, pytest and pre-commit checks.
3.  **Build Docker Compose:** Start web, API, PostgreSQL and Redis; add
    health checks and environment templates.
4.  **Add CI:** Run linting, type checks and unit tests on every pull
    request.

### Phase 2 --- Workflow contract

5.  **Define the Pydantic models:** Implement WorkflowDefinition,
    WorkflowNode, WorkflowEdge, NodePosition and typed node
    configurations.
6.  **Build graph validation:** Check unique IDs, edge references, node
    schemas, trigger count and DAG cycles.
7.  **Create database migrations:** Add workflows and workflow_versions
    tables, workspace ownership and draft revision tracking.
8.  **Implement workflow CRUD:** Create, read, update and list workflows
    with tests for invalid input and ownership.

### Phase 3 --- First execution

9.  **Implement the node registry:** Register trigger.manual,
    data.transform and action.mock_email with typed handlers.
10. **Build the synchronous executor:** Execute a validated linear graph
    in dependency order and return structured node results.
11. **Persist execution records:** Add workflow_runs and node_runs with
    status, output, timestamps and error details.
12. **Add the background worker:** Queue executions using Redis and
    Celery; make run creation idempotent.

### Phase 4 --- First complete UI

13. **Build the workflow editor:** Add React Flow nodes, edges, node
    selection, configuration forms and save operations.
14. **Add manual test runs:** Submit sample JSON and display each node's
    result and execution status.
15. **Add publishing:** Validate and snapshot the workflow before
    allowing it to run as a published version.
16. **Create the demo workflow:** Demonstrate a manual trigger, data
    transformation and mock email action end to end.

### Recommended build milestones

  Milestone   Target   Deliverable
  ----------- -------- -----------------------------------------------------
  M1          Week 1   Monorepo, Compose, CI and database
  M2          Week 2   Workflow contracts, CRUD and validation
  M3          Week 3   Execution engine, worker and persisted logs
  M4          Week 4   Visual editor and manual execution
  M5          Week 5   AI generation, model adapter and structured output
  M6          Week 6   Approval gates, reliability tests and polished demo

Treat these as planning estimates for a focused project, not guaranteed
deadlines. If you're working around your apprenticeship, prioritise the
end-to-end workflow before adding advanced integrations.

## 9. Engineering decisions that will matter in interviews

Create short architecture decision records as you work:

-   **ADR-001:** Modular monolith versus microservices.
-   **ADR-002:** Versioned JSON workflow definitions.
-   **ADR-003:** DAG execution and deterministic scheduling.
-   **ADR-004:** AI provider abstraction and structured output
    validation.
-   **ADR-005:** Background execution, retries and idempotency.
-   **ADR-006:** Human approval and safe resumption.
-   **ADR-007:** Local-first deployment with portable infrastructure.

These documents will help you explain why you made decisions, what
alternatives you considered and what trade-offs you accepted.

For AI quality, build a small evaluation dataset of representative
customer enquiries. Track classification accuracy, valid
structured-output rate, latency and cost. Avoid claiming time saved or
accuracy improvements until you have actually measured them.

## 10. Definition of done for the MVP

FlowPilot v1 is ready to demonstrate when:

-   A new developer can start the stack using documented setup
    instructions.
-   A user can create and visually edit a workflow.
-   A natural-language prompt generates an editable, validated workflow
    proposal.
-   A published workflow executes asynchronously against a fixed
    version.
-   AI output is schema-validated, and failures are visible and
    recoverable.
-   Approval gates prevent protected actions from executing prematurely.
-   Execution history shows node-level outcomes and timing.
-   Automated tests cover graph validation, branching, retries, approval
    and workspace isolation.
-   CI passes, and a recorded demonstration shows the complete
    customer-enquiry workflow.

**My recommendation for your very first coding session:** initialise the
monorepo, get Next.js and FastAPI running together through Docker
Compose, add PostgreSQL and Redis, and make the CI pipeline pass. Then
implement the workflow contract before building the visual editor.

That gives you a clean engineering foundation and a clear path from a
working skeleton to a portfolio-quality AI product.

------------------------------------------------------------------------

## User

copy this whole history chat into a md file

## Assistant

This Markdown export contains the FlowPilot discussion and product
specification in one file. The original chat's inline image previews are
represented by notes rather than embedded image files.
