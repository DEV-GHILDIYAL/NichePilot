# System architecture (proposed)

## Boundaries

V1 is planned as a Python/FastAPI modular monolith, a React/TypeScript dashboard, PostgreSQL, and a worker process using the same backend package. Phase 1 implements only the FastAPI account module and PostgreSQL persistence; Docker Compose currently runs only the database. The [roadmap](../development/roadmap.md) governs later delivery.

The API serves account configuration, review actions, and read models. Domain modules own rules; workflows coordinate them. The worker claims durable jobs, records state transitions, and invokes adapters. The dashboard reads persisted state instead of depending on worker logs. Modules should communicate through explicit application interfaces and IDs, not each other's database internals.

Planned backend domains: `accounts` (identity and Niche DNA), `trends`, `strategy`, `content`, `media`, `publishing`, `analytics`, `workflows`, and shared infrastructure for persistence, adapters, configuration, and telemetry. These names are proposed code boundaries, not directories to create in Phase 0. The frontend will organize account views and system views around the [dashboard IA](dashboard.md).

## Initial deployment and growth

One account and one host can run API, worker, PostgreSQL, and local media storage. PostgreSQL holds durable jobs and state; the scheduler only enqueues due work. Jobs are claimed atomically, have leases, attempt limits, idempotency keys, and recovery after worker loss. Do not assume exactly-once execution. Redis is deferred until measured contention or throughput needs it. Horizontal workers and shared object storage are later changes, while account IDs, adapter interfaces, and durable workflow records are designed now.

External boundaries are described in [integrations](integrations.md). Media processing is in [media pipeline](media-pipeline.md); account-owned entities and lifecycle states are in [domain model](domain-model.md). [Security controls](security-and-controls.md) gate side effects; [observability](observability.md) makes each step inspectable.

## Repository shape after Phase 0

`backend/app/accounts/` owns account, Niche DNA, and event contracts; `backend/migrations/` contains the schema migration; `backend/tests/` holds tests. Future work may add `frontend/` and `infra/` when their phases begin. The worker remains deferred.
