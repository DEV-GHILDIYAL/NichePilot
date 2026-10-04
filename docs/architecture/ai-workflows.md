# AI workflows and prompts

Logical roles share a workflow orchestrator; they are not separate services. Each step reads account-owned context, emits validated structured results, and records a run and decision summary. The [domain model](domain-model.md) defines persistence; [observability](observability.md) defines inspectability.

1. **Scout:** collect permitted signals through trend adapters; normalize and deduplicate.
2. **Niche Guardian:** apply hard forbidden-topic rules, score relevance against a specific Niche DNA revision, and explain an acceptable niche transformation or reject it. A global trend alone is insufficient.
3. **Strategist:** rank eligible opportunities using strategy, recent content, limits, and evidence; choose or decline.
4. **Writer:** produce structured hooks, scripts, captions, and metadata tied to the chosen idea.
5. **Creator:** turn a content specification into assets through the [media pipeline](media-pipeline.md).
6. **Critic:** assess niche fit, originality/repetition, clarity, quality, personality, and policy; return dimension scores and actionable reasons. Deterministic policy and asset checks remain authoritative.
7. **Publisher:** consume approved scheduled content only; use the supported integration and record attempts.
8. **Analyst:** compare metric snapshots with prior performance and propose bounded strategy adjustments. It cannot rewrite Niche DNA.

## Prompt contract

Store production prompts in role-named, versioned files when code begins, with input and output schema versions and tests. Each run records prompt version, model/provider, schema version, Niche DNA revision, input references, validated output, usage, and concise decision summary. Inject account context explicitly, with a size budget and source labels. Reject malformed output or retry within a bound; never silently parse arbitrary prose as an action. Avoid storing giant raw prompts or sensitive data by default.

The orchestrator owns transitions, deadlines, retries, and idempotency. A failed step must not advance the content lifecycle. Human approval, dry-run, and stop controls are specified in [security and controls](security-and-controls.md). The first runnable slice should use fake adapters and prove one traceable cycle before live services.
