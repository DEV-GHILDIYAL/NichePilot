# Integration boundaries

Adapters normalize external data and errors; domain modules must not depend on vendor payloads. Build only interfaces needed by an implemented use case. Provider configuration and credentials are account scoped where applicable, and fake adapters are first-class test tools.

- **Trend source:** fetch bounded signals with source ID, observed time, canonical URL/identifier, evidence, and quota metadata. Normalize before deduplication and [Niche Guardian evaluation](ai-workflows.md). Sources may later include public feeds, APIs, and manual input after terms and availability are checked.
- **AI:** narrow text, image, and TTS operations as required. Inputs/outputs have schemas and versions; calls report provider/model, latency, token/credit usage, error class, and estimated cost. A future video provider uses the [media specification](media-pipeline.md).
- **Media storage:** store/read/delete through a URI and metadata contract; local first, S3-compatible later. Access control and retention remain account aware.
- **Publishing:** Instagram is the first concrete adapter, using supported Meta/Instagram APIs only. Before implementation, verify current permissions, eligible account type, media requirements, quotas, and review requirements against official documentation. Do not automate a browser to mimic a person. Other platforms are future adapters, not V1 code.
- **Analytics:** fetch platform metric snapshots with collection time and source identity; missing or delayed metrics must remain distinguishable from zero.

Use bounded timeouts and retries with backoff for transient errors; classify authentication, quota, validation, and permanent failures separately. Record provider attempts and quota usage in [observability](observability.md). Publication retries require idempotency/reconciliation and [safety gates](security-and-controls.md). No adapter may silently fall back from dry-run to live behavior.
