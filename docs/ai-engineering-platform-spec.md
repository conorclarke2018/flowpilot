# AI Engineering Platform — SaaS Product Specification

**Status:** Product concept / MVP planning  
**Target:** Developers, software teams, engineering managers and small-to-medium SaaS companies  
**Primary goal:** Build a commercially viable SaaS while demonstrating strong software engineering, AI, cloud, DevOps and distributed-systems skills.

---

## 1. Product Overview

### Working name

**AI Engineering Platform**

A multi-tenant SaaS platform that connects to GitHub/GitLab repositories and uses AI to help engineering teams understand, review, maintain and improve their software.

The platform combines:

- AI codebase search and Q&A
- AI-powered pull-request reviews
- AI-generated engineering tickets
- Engineering health scoring
- Dependency and security monitoring
- Automatic documentation
- Team engineering knowledge

### Product positioning

> **An AI engineering assistant that understands your entire codebase and helps your team build, review and maintain software.**

The product should not be positioned as simply another AI chatbot. The core value is **deep integration with a team's real repositories, development workflow and engineering data**.

---

# 2. Problem

Software teams commonly struggle with:

- Developers spending time understanding unfamiliar code
- Knowledge being trapped in individual developers' heads
- Pull requests taking too long to review
- Technical debt accumulating unnoticed
- Missing or outdated documentation
- Security and dependency issues
- Poor test coverage
- Repetitive engineering tasks
- Difficulty understanding why architectural decisions were made
- New developers taking a long time to become productive

The platform should reduce these costs by continuously analysing the team's software and turning the analysis into useful engineering actions.

---

# 3. Target Customers

## Primary customers

### Small software teams

Approximately 2–25 developers.

Typical characteristics:

- SaaS companies
- Startups
- Internal software teams
- Agencies
- Teams without dedicated platform/DevOps staff

### Secondary customers

- Larger engineering organisations
- Technical leads
- Engineering managers
- CTOs
- Development agencies
- Open-source teams

---

# 4. Core User Journey

```text
Sign up
   |
   v
Create organisation
   |
   v
Create project
   |
   v
Connect GitHub/GitLab
   |
   v
Select repository
   |
   v
Repository ingestion
   |
   v
Code analysis
   |
   +-------------------+
   |                   |
   v                   v
Code index          Engineering analysis
   |                   |
   v                   v
AI Assistant       Health / Issues
   |
   v
Developer workflow
   |
   +---------+-----------+-------------+
   |         |           |             |
   v         v           v             v
Ask AI    PR Review   AI Tickets   Documentation
```

---

# 5. MVP

The first release should stay focused.

## MVP features

### Authentication

- Email/password authentication
- OAuth
- Session management
- Password reset
- Email verification

### Organisations

- Create organisation
- Invite users
- Organisation membership
- Basic roles

### Projects

- Create project
- Add repository
- Project dashboard
- Project settings

### GitHub/GitLab integration

- OAuth connection
- Repository selection
- Repository synchronisation
- Webhook support
- Branch selection

### Code ingestion

- Clone/fetch repository
- Parse source files
- Ignore generated files
- Ignore node_modules, .venv, .next, build artefacts, etc.
- Chunk source code
- Generate embeddings
- Store vectors

### AI Codebase Assistant

Users can ask questions such as:

- "Where is authentication handled?"
- "How does a user get created?"
- "What calls the payment service?"
- "Explain the image-processing pipeline."
- "Where is Redis used?"
- "What would break if this database table changed?"

The assistant should return answers with references to relevant files and code sections.

### AI Pull Request Review

On pull request creation/update:

- Fetch diff
- Analyse changed code
- Identify potential bugs
- Identify security issues
- Identify performance issues
- Identify missing tests
- Provide review summary
- Post review comments/status back to GitHub/GitLab

### AI-generated tickets

Allow users to convert AI findings into issues.

Example:

```text
Title:
Add rate limiting to authentication endpoints

Severity:
High

Description:
The login endpoint currently has no request throttling.

Suggested solution:
- Add Redis-backed rate limiting
- Return HTTP 429 on excessive requests
- Add integration tests

Estimated complexity:
Medium
```

---

# 6. Post-MVP Features

## Engineering Health Score

Each repository receives an overall score.

Example:

```text
Engineering Health

87 / 100

Security       92
Testing        81
Performance    89
Dependencies   94
Architecture   84
Code Quality   83
```

The score should be explainable and based on measurable signals.

---

## Dependency Monitoring

Detect:

- Outdated packages
- Known vulnerabilities
- Major version upgrades
- Deprecated dependencies

Provide:

- Severity
- Affected component
- Recommended update
- AI-generated explanation
- Remediation ticket

---

## AI Documentation

Generate and maintain:

- Architecture overview
- API documentation
- Database documentation
- Deployment documentation
- Environment variables
- Service relationships
- Troubleshooting guides

Documentation should be regenerated or flagged for review when relevant code changes.

---

## Team Knowledge

Combine:

```text
Source Code
+
Pull Requests
+
Issues
+
Documentation
+
Architecture
```

into a searchable engineering knowledge base.

Example questions:

- "Why was Redis introduced?"
- "Why does this service use a queue?"
- "Who worked on the authentication system?"
- "What changed in the payment service last month?"

---

# 7. SaaS Multi-Tenancy

The application must be designed as a multi-tenant SaaS from the beginning.

```text
                    SaaS
                      |
          +-----------+-----------+
          |                       |
     Organisation A         Organisation B
          |                       |
     +----+----+             +----+----+
     |         |             |         |
   User A    User B        User C    User D
```

## Tenant isolation

Every organisation-owned resource must have an `organisation_id` / tenant identifier.

Examples:

- users
- projects
- repositories
- issues
- AI conversations
- embeddings
- jobs
- usage records
- billing records

Never rely solely on frontend filtering for tenant isolation.

The backend must enforce tenant boundaries.

---

# 8. Roles and Permissions

Initial roles:

### Owner

- Manage organisation
- Manage billing
- Manage users
- Manage integrations
- Delete organisation

### Admin

- Manage projects
- Manage repositories
- Manage users

### Developer

- View projects
- Ask AI
- Review code
- Create tickets

### Viewer

- Read-only access

Future:

- Custom roles
- Fine-grained permissions
- Enterprise RBAC

---

# 9. Proposed Technology Stack

## Frontend

- Next.js
- TypeScript
- React
- Mantine
- TanStack Query
- Zod

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

## Database

- PostgreSQL

## Cache / jobs

- Redis
- AWS SQS

## Vector search

Initial:

- FAISS for local development

Production:

- Qdrant or another managed/self-hosted vector database

## AI

Primary:

- Qwen
- vLLM
- Hugging Face

Optional providers:

- OpenAI
- Anthropic
- AWS Bedrock

The application should use a provider abstraction so models can be changed without rewriting application logic.

## Infrastructure

- Docker
- AWS
- Terraform
- Kubernetes/EKS

## CI/CD

- GitHub Actions or GitLab CI

## Observability

- Prometheus
- Grafana
- OpenTelemetry
- Structured application logging

## Billing

- Stripe

---

# 10. High-Level Architecture

```text
                         Internet
                            |
                            v
                       CloudFront
                            |
                            v
                         Next.js
                            |
                            v
                       API Gateway
                            |
                            v
                         FastAPI
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
      PostgreSQL          Redis              S3
          |                 |
          |                 v
          |                SQS
          |                 |
          |        +--------+--------+
          |        |        |        |
          |        v        v        v
          |      Worker   Worker   Worker
          |        |        |        |
          |        +--------+--------+
          |                 |
          |                 v
          |              AI Layer
          |                 |
          |          +------+------+
          |          |             |
          |          v             v
          |       Embeddings      LLM
          |          |             |
          |          v             v
          |       Qdrant         vLLM
          |                        |
          |                       GPU
          |
          v
       Billing
          |
          v
        Stripe
```

---

# 11. Core Services

The initial application should remain a modular monolith where practical.

Avoid unnecessary microservices early.

## API

Responsibilities:

- Authentication
- Organisations
- Users
- Projects
- Repositories
- Conversations
- Issues
- Billing
- API keys

## Repository Service

Responsibilities:

- GitHub/GitLab integration
- Repository synchronisation
- Webhooks
- Branch handling
- Commit metadata

## Ingestion Worker

Responsibilities:

- Fetch repository
- Parse files
- Filter irrelevant files
- Chunk source
- Generate embeddings
- Store vectors

## AI Service

Responsibilities:

- Prompt construction
- Context retrieval
- Model routing
- Streaming responses
- Token/usage tracking
- AI provider abstraction

## PR Review Worker

Responsibilities:

- Receive webhook
- Fetch PR
- Analyse diff
- Run AI review
- Store result
- Publish review

## Issue Service

Responsibilities:

- AI findings
- Manual issues
- Status
- Assignment
- Priority
- AI-generated remediation

---

# 12. Database Model

Initial entities:

```text
User
Organisation
OrganisationMember
Project
Repository
RepositoryBranch
RepositoryCommit
PullRequest
PullRequestReview
Issue
IssueComment
AIConversation
AIMessage
CodeChunk
Embedding
Job
UsageRecord
Subscription
Integration
AuditLog
```

Relationship example:

```text
Organisation
    |
    +--- Members
    |
    +--- Projects
           |
           +--- Repositories
           |       |
           |       +--- Commits
           |       +--- Pull Requests
           |
           +--- Issues
           |
           +--- AI Conversations
```

---

# 13. AI/RAG Architecture

```text
Repository
    |
    v
File filtering
    |
    v
Language detection
    |
    v
AST / code parsing
    |
    v
Chunking
    |
    v
Embedding model
    |
    v
Vector database
    |
    v
User question
    |
    v
Query embedding
    |
    v
Semantic retrieval
    |
    v
Context ranking
    |
    v
Prompt construction
    |
    v
LLM
    |
    v
Answer + source references
```

The assistant should cite source files whenever possible.

Example:

```text
Authentication is handled by the AuthMiddleware.

Relevant files:
- backend/auth/middleware.py
- backend/auth/service.py
- backend/routes/login.py
```

---

# 14. Background Job Architecture

Long-running operations should not block API requests.

```text
API
 |
 v
Create Job
 |
 v
SQS
 |
 +----> Repository Worker
 |
 +----> Embedding Worker
 |
 +----> AI Review Worker
 |
 +----> Documentation Worker
 |
 +----> Security Worker
```

Jobs should support:

- Queuing
- Retries
- Failure states
- Dead-letter queues
- Progress tracking
- Cancellation where practical
- Idempotency

---

# 15. Security Requirements

Security is a core product requirement because the platform handles private source code.

## Authentication

- Secure password hashing
- OAuth
- MFA eventually
- Session expiry
- Secure cookies/tokens

## Authorisation

- Organisation-level isolation
- RBAC
- Server-side permission checks

## Repository security

- Never expose repository credentials
- Encrypt secrets
- Short-lived tokens where supported
- Minimise OAuth scopes

## AI security

Protect against:

- Prompt injection from source code
- Data exfiltration
- Cross-tenant retrieval
- Malicious repository content
- Secrets being included in AI context

## Infrastructure

- Private subnets
- IAM least privilege
- Secrets Manager
- Encryption at rest
- Encryption in transit
- Security groups
- Audit logs

---

# 16. SaaS Billing

Initial plans:

## Free

- 1 repository
- 2 users
- Limited AI usage
- Limited PR reviews

## Team

Target: approximately £15–£25/user/month

- Multiple repositories
- AI code reviews
- AI assistant
- AI ticket generation
- Dependency monitoring

## Business

Target: approximately £30–£50/user/month

- Advanced security
- Larger AI limits
- SSO
- Audit logs
- Advanced analytics
- Priority processing

## Enterprise

Custom pricing.

Potential features:

- Private deployment
- Dedicated inference
- VPC deployment
- Self-hosting
- SSO/SAML
- Advanced RBAC
- Custom retention
- Air-gapped deployment

Pricing is provisional and should be validated through customer research.

---

# 17. Usage Metering

Track:

```text
AI requests
Input tokens
Output tokens
Repository size
Indexed files
PR reviews
Background jobs
Storage
Users
```

Usage records should be linked to:

```text
Organisation
Project
User
Feature
Model
Timestamp
```

This allows future usage-based pricing.

---

# 18. API Design

Example endpoints:

```text
POST   /api/v1/auth/login
POST   /api/v1/auth/logout

GET    /api/v1/organisations
POST   /api/v1/organisations

GET    /api/v1/projects
POST   /api/v1/projects

GET    /api/v1/repositories
POST   /api/v1/repositories/connect

POST   /api/v1/repositories/{id}/sync

GET    /api/v1/conversations
POST   /api/v1/conversations

POST   /api/v1/conversations/{id}/messages

GET    /api/v1/pull-requests
GET    /api/v1/pull-requests/{id}/reviews

POST   /api/v1/issues
PATCH  /api/v1/issues/{id}

GET    /api/v1/health
GET    /api/v1/usage
```

Webhooks:

```text
POST /api/v1/webhooks/github
POST /api/v1/webhooks/gitlab
POST /api/v1/webhooks/stripe
```

---

# 19. Frontend Structure

```text
app/
├── dashboard/
├── organisations/
├── projects/
├── repositories/
├── assistant/
├── reviews/
├── issues/
├── health/
├── settings/
├── billing/
└── auth/
```

Important UI areas:

### Dashboard

- Engineering health
- Recent reviews
- Open issues
- AI usage
- Repository activity

### AI Assistant

- Chat interface
- Source references
- Conversation history
- Project/repository selection

### PR Reviews

- Review status
- Findings
- Severity
- File references
- Suggested fixes

### Engineering Health

- Score
- Trend
- Security
- Testing
- Dependencies
- Architecture
- Code quality

---

# 20. Repository Structure

Recommended monorepo:

```text
ai-engineering-platform/
│
├── apps/
│   ├── web/
│   │   └── Next.js
│   │
│   └── api/
│       └── FastAPI
│
├── workers/
│   ├── ingestion/
│   ├── embeddings/
│   ├── pr-review/
│   ├── documentation/
│   └── security/
│
├── packages/
│   ├── shared-types/
│   └── ai/
│
├── infrastructure/
│   └── terraform/
│
├── docker/
│
├── tests/
│
├── docs/
│
├── docker-compose.yml
├── README.md
└── Makefile
```

---

# 21. Development Roadmap

## Phase 1 — Foundation

- [ ] Repository creation
- [ ] Next.js application
- [ ] FastAPI application
- [ ] PostgreSQL
- [ ] Docker Compose
- [ ] Database migrations
- [ ] Authentication
- [ ] Basic UI

## Phase 2 — SaaS Core

- [ ] Organisations
- [ ] Organisation members
- [ ] Roles
- [ ] Projects
- [ ] Repository model
- [ ] Tenant isolation
- [ ] Audit logging

## Phase 3 — Git Integration

- [ ] GitHub OAuth
- [ ] GitLab OAuth
- [ ] Repository selection
- [ ] Repository synchronisation
- [ ] Webhooks
- [ ] Commit tracking

## Phase 4 — AI Code Search

- [ ] File filtering
- [ ] Code parsing
- [ ] Chunking
- [ ] Embeddings
- [ ] Vector database
- [ ] Retrieval
- [ ] AI chat
- [ ] Source references

## Phase 5 — AI PR Reviews

- [ ] PR webhook
- [ ] Diff retrieval
- [ ] Review worker
- [ ] AI analysis
- [ ] Severity classification
- [ ] GitHub/GitLab comments

## Phase 6 — Engineering Issues

- [ ] AI findings
- [ ] Issue creation
- [ ] Issue status
- [ ] Assignment
- [ ] AI remediation suggestions

## Phase 7 — Production Infrastructure

- [ ] CI/CD
- [ ] AWS
- [ ] Terraform
- [ ] S3
- [ ] RDS
- [ ] SQS
- [ ] Redis
- [ ] Secrets Manager
- [ ] CloudWatch

## Phase 8 — Observability

- [ ] Structured logs
- [ ] Metrics
- [ ] Prometheus
- [ ] Grafana
- [ ] OpenTelemetry
- [ ] Error tracking

## Phase 9 — Billing

- [ ] Stripe
- [ ] Free plan
- [ ] Team plan
- [ ] Business plan
- [ ] Usage tracking
- [ ] Usage limits
- [ ] Subscription management

## Phase 10 — Kubernetes

- [ ] Kubernetes deployment
- [ ] Helm
- [ ] Horizontal scaling
- [ ] Worker autoscaling
- [ ] Health checks
- [ ] GPU workloads
- [ ] Production deployment

---

# 22. Testing Strategy

## Backend

- Unit tests
- API tests
- Integration tests
- Database tests
- Authentication tests
- Tenant-isolation tests

## Frontend

- Component tests
- Integration tests
- End-to-end tests

## AI

- Retrieval quality tests
- Prompt regression tests
- Hallucination checks
- Source attribution tests
- Security/prompt-injection tests

## Infrastructure

- Terraform validation
- Terraform plan checks
- Container scanning
- Dependency scanning

Target:

> Every production feature should have automated tests before release.

---

# 23. Observability

Monitor:

### Application

- Request count
- Latency
- Error rate
- HTTP status codes

### AI

- Model latency
- Tokens
- Cost
- Retrieval latency
- Retrieval quality
- Failed generations

### Workers

- Queue depth
- Job duration
- Failed jobs
- Retry count
- Worker utilisation

### Infrastructure

- CPU
- Memory
- Disk
- Network
- GPU utilisation

---

# 24. Performance Targets

Initial targets are provisional.

### API

- p95 standard API response < 300ms

### AI search

- Retrieval < 500ms where practical
- Streaming response to user as soon as generation begins

### Repository ingestion

- Process asynchronously
- Show progress to user

### PR review

- Initial review result target < 2 minutes for typical PRs

These should be measured rather than assumed.

---

# 25. Product Metrics

Track:

### Acquisition

- Sign-ups
- Connected repositories
- Activated organisations

### Engagement

- AI questions
- PR reviews
- Issues generated
- Weekly active users
- Monthly active users

### Retention

- Organisation retention
- User retention
- Repository retention

### Revenue

- MRR
- ARR
- ARPU
- Conversion rate
- Churn

### AI economics

- AI cost per organisation
- AI cost per review
- Tokens per request
- Gross margin

---

# 26. Portfolio / CV Value

The project should demonstrate:

## Software engineering

- Python
- FastAPI
- TypeScript
- Next.js
- PostgreSQL
- Redis
- REST APIs
- Testing

## Cloud

- AWS
- VPC
- ECS/EKS
- RDS
- S3
- SQS
- IAM
- CloudWatch

## DevOps

- Docker
- Kubernetes
- Terraform
- CI/CD

## AI

- LLMs
- RAG
- embeddings
- vector search
- vLLM
- model serving

## Architecture

- Multi-tenancy
- Event-driven processing
- Distributed workers
- Scalability
- Observability
- Security

---

# 27. Portfolio Goal

The finished project should be deployable publicly and have a professional README containing:

- Product overview
- Live demo
- Architecture diagram
- Technology stack
- Screenshots
- API documentation
- Database architecture
- AI/RAG architecture
- Infrastructure architecture
- Performance benchmarks
- Testing results
- Security considerations
- Deployment instructions
- Technical decisions

The project should demonstrate that the developer can **design, build, deploy and operate a real SaaS product**.

---

# 28. Long-Term Product Vision

The eventual product can evolve from:

> AI code assistant

into:

> **AI engineering operating system for software teams.**

Potential future capabilities:

- Automatic sprint planning
- Engineering analytics
- Technical debt forecasting
- AI-generated implementation plans
- Automated test generation
- Automated documentation
- Architecture visualisation
- Incident analysis
- Log analysis
- Production error analysis
- Cost optimisation
- Security monitoring
- AI coding agents
- Private enterprise AI models

---

# 29. Initial Success Criteria

The MVP is successful when a new user can:

1. Create an account
2. Create an organisation
3. Connect GitHub/GitLab
4. Import a repository
5. Wait for indexing to complete
6. Ask questions about their codebase
7. Receive answers with source references
8. Open a pull request
9. Receive an AI review
10. Convert a finding into an engineering issue
11. Invite another developer
12. View project activity

The product should feel like a real SaaS application rather than a collection of AI demos.

---

# 30. Recommended Build Philosophy

### Build the simplest architecture that can scale.

Do **not** begin with 15 microservices.

Start with:

```text
Next.js
   |
FastAPI
   |
PostgreSQL
   |
Redis
   |
Background workers
```

Then introduce:

```text
SQS
AWS
Terraform
Kubernetes
vLLM
```

only as the product requires them.

### Priorities

1. Product usability
2. Security
3. Correctness
4. Testing
5. Observability
6. Performance
7. Scalability

The goal is to build a SaaS that is **useful first and technically impressive second**.
