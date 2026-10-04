# ADR 0005: Auditable decisions and explicit publishing gates

Status: Accepted for the Phase 0 design

## Context

Autonomous content can fail, drift, duplicate posts, or consume quotas. An administrator needs to understand actions and safely halt them.

## Decision

Persist linked workflow/agent runs, concise decisions, validations, and publication attempts. Default to fake publishing, dry-run, manual approval, and disabled automation. Recheck kill switch, account pause, mode, approval, validation, limits, and duplicate status immediately before a supported API call. See [observability](../architecture/observability.md) and [security controls](../architecture/security-and-controls.md).

## Consequences

Storage and code paths increase, but decisions become reviewable and side effects controllable. Do not store private chain-of-thought. Uncertain publication outcomes need reconciliation before retry.
