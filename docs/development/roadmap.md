# Roadmap

Phases are delivery slices, not fixed dates. Advance when the exit condition is met; keep application work out of Phase 0.

0. **Foundation (complete):** architecture, context router, ADRs, workflows, safety defaults, and repository skills.
1. **Backend and Account/Niche DNA (complete):** account-scoped models and immutable revisions, PostgreSQL migration, protected API, pause/resume, and event history. Isolation and revision tests pass; no live publishing.
2. **Simulated workflow and early dashboard:** worker, fake-provider cycle, account modes and limits, plus read-only workflow/decision timeline. Exit: an administrator can inspect current/next work and safely pause it; the fake cycle is traceable.
3. **Trends and strategy:** source adapters, normalization/deduplication, Niche Guardian, and opportunity ranking. Exit: accepted/rejected signals have reproducible reasons tied to DNA versions.
4. **Content and media:** versioned writer/critic contracts, free-first media assembly, asset validation and preview. Exit: a reviewed candidate can be produced and rejected safely.
5. **Scheduling and review:** approval queue, calendar, quotas, duplicate prevention, and dry-run publisher. Exit: a full dry-run cycle has auditable gates and bounded retries.
6. **Instagram publishing:** verify current supported API requirements, obtain credentials/permissions, implement adapter and reconciliation. Exit: controlled live test succeeds without bypassing gates.
7. **Analytics and learning:** metric snapshots, insights, bounded strategy proposals, and dashboard trends. Exit: applied changes remain within Niche DNA and are reversible/auditable.
8. **Operations and scale:** deployment hardening on the intended host, backups/recovery, retention, health/usage alerts, then multi-account load and shared storage/queue only when needed. Exit: operational checks and isolation tests match the deployment target.

The next [delivery slice](../PROJECT_CONTEXT.md) should establish the simulated cycle before adding live providers. Later phases may be split when implementation reveals risk.
