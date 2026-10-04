# Conceptual domain model

The conceptual model below covers future domains. Phase 1 implements only Account, NicheDNARevision, and AccountChangeEvent in PostgreSQL. Every account-owned record carries `account_id`; joins and queries must enforce it. Cross-account learning is out of scope.

## Identity and strategy

- **Account:** platform identity, status, operating mode, limits, schedule, and references to credentials. Status includes active or paused; a global stop applies above it.
- **NicheDNARevision:** immutable version of niche, target audience, language, tone, content pillars, forbidden topics, and allowed transformations of trends. One revision is active per account. Publication decisions retain the revision ID used.
- **StrategyRevision:** adjustable mix, formats, cadence, and source preferences within an active Niche DNA revision. Analyst suggestions are separate from applied revisions; niche changes require administrator action.
- **TrendSourceConfig:** account-specific sources, filters, and quotas.

Phase 1 accounts start paused. A non-null platform handle is unique per platform. `PATCH /api/v1/accounts/{account_id}` requires `expected_version` to reject stale metadata changes. Niche DNA content is immutable at the database layer; a new revision is created and activated transactionally after checking the expected active revision number. A composite foreign key prevents an account from pointing to another account's revision. The service records `AccountChangeEvent` for creation, metadata updates, pause/resume, and revision activation. No event is written for a failed or unchanged operation.

The protected `/api/v1/accounts/{account_id}/events` endpoint orders events by `occurred_at DESC, id DESC` and returns `items` and an opaque `next_cursor` for stable paging (default 25, maximum 100). Account and revision lists use bounded limit/offset in this phase. These are current contracts; there is no workflow or content API yet.

## Content lineage

`TrendSignal` records normalized source evidence and deduplication identity. An account's `TrendEvaluation` records niche score, disposition, concise reason, and Niche DNA revision. Accepted signals may lead to `ContentIdea`; a `ContentDraft` holds versioned script/caption/asset specification; `ContentAsset` holds URI, type, checksum, provenance, and validation. `ContentEvaluation` scores a particular draft and asset set. Rejections remain visible. `ScheduleSlot` reserves a time; `Post` connects an approved version to its planned and eventual platform identity. `PublicationAttempt` records each API attempt and uncertain outcomes. `MetricSnapshot` is time-stamped platform data. `Insight` is evidence-backed analysis; `StrategyRevision` records any applied change.

## Execution and audit

`WorkflowRun` has account, trigger, state, timestamps, and parent/correlation IDs. `AgentRun` identifies logical role, prompt/schema versions, bounded input/output references, provider, usage, result, and failure. `Decision` records decision type, subject, rule/model version, scores, concise rationale, and resulting action. These are audit summaries, never private chain-of-thought. See [observability](observability.md).

## Lifecycles and invariants

- Trend evaluation: `pending → accepted | rejected | error`; reevaluation creates another version rather than erasing history.
- Idea/draft: `proposed → selected → drafted → evaluated → approved | rejected`; revision creates a new draft version.
- Post: `approved → scheduled → publishing → published | failed | uncertain | cancelled`. `uncertain` requires reconciliation before retry to avoid duplicate publication.
- Workflow/job: `queued → running → succeeded | failed | cancelled`, with bounded attempts recorded separately.
- Only a content version that passed current validation and the applicable approval gate may be scheduled or published. Pause, kill switch, quotas, duplicate checks, and platform configuration are checked again immediately before the external call.

Deletion and retention policies are deferred to implementation, but audit lineage must survive ordinary edits and retries. See [AI workflows](ai-workflows.md) and [security controls](security-and-controls.md).
