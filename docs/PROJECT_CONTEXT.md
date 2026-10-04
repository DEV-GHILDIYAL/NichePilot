# Project context

**What:** NichePilot will manage autonomous AI creator accounts. Initial target: one Instagram account, with architecture for account isolation and later expansion. Niche DNA constrains all content and learning.

**Current state:** Phase 1 backend implements account configuration, immutable Niche DNA revisions, account change events, administrator bearer-token protection, PostgreSQL migration, and health endpoints. No frontend, worker, creator workflow, provider integration, or live publishing exists.

**Architecture direction:** The implemented backend is a FastAPI/Python modular foundation with PostgreSQL. A React/TypeScript dashboard, worker, provider adapters, media assembly, supported Instagram publishing, and explicit live gates remain planned. See [system architecture](architecture/system.md) and [ADRs](adr/README.md).

**Navigation:** [Documentation index](INDEX.md) routes by task. [Roadmap](development/roadmap.md) names the next milestones. [Development workflow](development/workflow.md) explains task records and validation.

**Limits and risks:** The admin token is a temporary server-side authorization boundary, not dashboard user authentication. Instagram permissions/formats and free-tier limits require verification later. Zero monthly cost is a target, not a guarantee. See [local commands](operations/environments.md).

**Next milestone:** A simulated creator workflow and worker in the next delivery slice, with fake providers and no live publishing. Do not begin without a new instruction.
