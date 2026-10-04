# Backend module

Phase 1 implements account configuration only. `app/main.py` owns HTTP routes, request IDs, health, and the replaceable administrator authorization dependency. `app/accounts/schemas.py` validates API contracts; `service.py` owns transactions and state changes; `models.py` maps the three account-owned tables. `migrations/` owns the PostgreSQL schema. The active revision foreign key and database trigger enforce ownership and revision immutability.

Account writes require a server-side bearer token. `PATCH /api/v1/accounts/{id}` requires `expected_version`; creating a Niche DNA revision requires `expected_active_revision_number`. Stale writes return 409. Account events are read newest first via an opaque cursor, default page size 25 and maximum 100. No route can publish content.

Use [local setup and commands](../docs/operations/environments.md) for migration, API startup, and checks. The [domain model](../docs/architecture/domain-model.md) explains invariants; [security controls](../docs/architecture/security-and-controls.md) define safe modes.
