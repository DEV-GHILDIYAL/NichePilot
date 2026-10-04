# ADR 0004: Narrow provider boundaries

Status: Accepted for the Phase 0 design

## Context

Free tiers, model quality, and platform capabilities can change. Domain logic should not inherit vendor payload formats or credentials.

## Decision

Place trend, AI, media-storage, publishing, and analytics calls behind narrow interfaces defined by implemented use cases. Normalize outputs and errors; ship fake adapters for tests and dry-runs. Do not build a universal plugin framework. See [integrations](../architecture/integrations.md) and [media pipeline](../architecture/media-pipeline.md).

## Consequences

Provider swaps remain possible and external calls are mockable. Each interface has maintenance cost, so add methods only for actual workflows. Paid video generation remains a future adapter subject to the same validation gates.
