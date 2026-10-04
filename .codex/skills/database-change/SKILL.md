---
name: database-change
description: Plan and implement NichePilot persistence model or migration changes. Use for account-scoped entities, lifecycle states, workflow jobs, audit records, and schema evolution.
---

# Database change

Read [domain model](../../../docs/architecture/domain-model.md), the affected repository/migrations, and tests. Identify account ownership, lifecycle invariants, existing rows, and rollback or forward-repair needs before changing schema.

- Keep account-owned records and joins scoped by `account_id`; preserve immutable revisions and audit lineage.
- Make migrations explicit and compatible with the deployment path; avoid destructive changes without a data plan.
- Test constraints and state transitions, including cross-account access denial, retry recovery, and existing-data behavior when relevant.
- Commit migration with model and query changes. Update the domain model for a changed conceptual contract; add an ADR only for a consequential architectural choice.
