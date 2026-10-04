# Dashboard information architecture

The dashboard is the administrator's view of persisted state and controls, not a substitute for operational logs. It must answer: what is happening, what happened, why, and what is next. No UI is implemented in Phase 0.

## Navigation

- **Overview:** active/paused account, current workflow, upcoming post, recent decisions and failures, usage, and health.
- **Accounts → account detail:** Niche DNA and strategy revisions; configured trend sources; trend evaluations; ideas and rejected reasons; drafts/assets and previews; review queue; calendar/posts; analytics and insights; agent activity; account controls.
- **System:** workflow runs and retries; provider status/quotas and estimated cost; publishing activity; structured logs and health; global controls and settings.

## Major journeys

1. Create an account, define Niche DNA, sources, limits, schedule, and operating mode; preview settings before activation.
2. Inspect a signal and follow its lineage through niche score, idea, draft, evaluation, media, approval, schedule, publication, metrics, and insight. Show the specific rule/prompt/config versions behind a decision.
3. Review and approve/reject a versioned content candidate; a changed draft needs reevaluation. Override a schedule without bypassing validation or publication gates.
4. Pause an account or all automation, inspect failed/uncertain publication attempts, and safely resume or reconcile.
5. Compare performance over time and inspect proposed versus applied strategy changes, with Niche DNA changes reserved for an administrator.

Read models should paginate and filter by account, state, date, and correlation ID. Redact credentials and large raw AI payloads. Distinguish no data, pending, failed, and stale states. Control authorization and audit are in [security and controls](security-and-controls.md); event fields are in [observability](observability.md).
