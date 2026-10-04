# ADR 0002: Account isolation and versioned Niche DNA

Status: Accepted for the Phase 0 design

## Context

The platform begins with one account but must later host several. Learning should improve performance without changing a creator's niche or allowing another account's data to influence it silently.

## Decision

Give each account independent configuration, credentials, content, runs, metrics, and learning. Persist immutable Niche DNA revisions; decisions reference the revision used. Analyst outputs may propose bounded strategy changes but cannot edit Niche DNA. See [domain model](../architecture/domain-model.md).

## Consequences

Every query, job, and cache key must respect account scope. Revisions add data volume but make past decisions explainable. Cross-account learning requires a future explicit design and consent boundary.
