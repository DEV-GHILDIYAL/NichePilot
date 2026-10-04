# ADR 0001: Modular monolith for V1

Status: Accepted for the Phase 0 design

## Context

The first deployment targets one creator account on one host and a free-first budget. Logical agent roles need clear boundaries, but separate services would add deployment and tracing costs before scale is known.

## Decision

Use a FastAPI/Python modular monolith with explicit domain modules, a worker process from the same codebase, PostgreSQL, and a separate React/TypeScript dashboard. Do not create a service per agent. See [system architecture](../architecture/system.md).

## Consequences

Local development and deployment stay simpler, and transactions can cover core state transitions. Module interfaces and account IDs must remain clear to avoid a tangled monolith. Extract services only when measured load or ownership boundaries justify it.
