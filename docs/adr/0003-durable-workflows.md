# ADR 0003: Durable workflows before a dedicated queue

Status: Accepted for the Phase 0 design

## Context

Scheduled autonomous work needs restart recovery and visible retries. A separate queue service would increase initial operating cost and complexity for one account.

## Decision

Start with PostgreSQL-backed job/workflow state and a simple scheduler that enqueues due work. Workers claim jobs atomically using leases; steps have bounded attempts, deadlines, and idempotency keys. Introduce a dedicated queue only after measured need. See [system architecture](../architecture/system.md).

## Consequences

The database carries job load and needs careful claim/recovery tests. Execution is at least once, so side effects require idempotency and uncertain-result reconciliation. The first worker implementation must prove these invariants before live publishing.
