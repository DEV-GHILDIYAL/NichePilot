---
name: integration-change
description: Add or change NichePilot external trend, AI, storage, analytics, or publishing adapters. Use when provider contracts, credentials, quotas, retries, or API behavior change.
---

# Integration change

Read [integration boundaries](../../../docs/architecture/integrations.md), the affected adapter, its contract tests, and [security controls](../../../docs/architecture/security-and-controls.md). Verify current provider requirements from authoritative documentation when implementing an external API.

- Keep vendor formats and credentials inside the adapter. Return normalized results, usage, and classified errors to domain code.
- Bound timeouts, retries, rate limits, and cost; distinguish an uncertain external side effect from a safe retry.
- Preserve a fake/dry-run path and account scope. A configuration mistake must not switch silently to live publishing.
- Test mapping, authentication/quota/permanent failure, idempotency or reconciliation where relevant, and secret redaction without live side effects.
- Update the affected architecture or operations document when the contract or setup changes.
