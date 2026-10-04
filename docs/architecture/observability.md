# Observability and auditability

The source of truth for autonomous activity is durable, structured records that the dashboard can query. Application logs support diagnosis but do not replace those records. Avoid private chain-of-thought; record concise decision summaries, inputs/outputs or references, scores, versions, and outcomes.

Phase 1 implements `AccountChangeEvent` for account creation, metadata changes, pause/resume, and Niche DNA activation. `GET /api/v1/accounts/{account_id}/events` exposes newest-first cursor pagination for the future dashboard. HTTP logs include method, path, status, duration, and a generated request ID; they do not include authorization headers or request bodies. Workflow and agent run telemetry below remains planned.

## Trace model

Every trigger creates a `WorkflowRun` with account, trigger, correlation ID, status, timestamps, current/next step, and terminal reason. Each logical role call creates an `AgentRun` with role, prompt/schema/config versions, provider/model, status, duration, usage, and error class. Each consequential accept/reject/rank/approve/learn action creates a `Decision` linked to its subject and originating runs. Content and publication records preserve lineage described in the [domain model](domain-model.md).

The dashboard should expose a timeline from trend source to niche evaluation, idea, draft, critique, asset validation, schedule, publication attempt, metric snapshot, and strategy insight. Rejected and failed branches remain visible. Filters include account, time, status, provider, and correlation ID.

## Failures, retries, and usage

Record each job and provider attempt with attempt number, next retry, deadline, error class, sanitized message, and final disposition. Show stalled leases, exhausted retries, uncertain publication, and quota exhaustion as actionable states. Track request counts, tokens/credits, media duration/storage, quota remaining when supplied, and estimated spend by account, provider, operation, and time period. Mark estimates as estimates; missing price data must not appear as zero cost. Apply budgets and alerts before optional expensive operations.

Publishing activity shows approval state, configured mode, scheduled time, gate checks, every attempt, platform result ID, and reconciliation status. Logs use structured fields such as `account_id`, `workflow_run_id`, `agent_run_id`, `content_id`, provider, and operation. Redact credentials, sensitive personal data, large raw prompts, and raw provider responses by default.

## Health

Initial health checks cover API readiness, database connectivity, scheduler heartbeat, worker heartbeat/queue age, storage reachability, provider availability, recent workflow failure rate, and next scheduled work. Expose simple dashboard indicators and operator logs first; add metrics infrastructure only when operational need warrants it. See [dashboard](dashboard.md), [operations](../operations/environments.md), and [security and controls](security-and-controls.md).
