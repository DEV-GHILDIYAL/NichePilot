# Testing strategy

Test the narrowest useful layer first. Domain unit tests cover Niche DNA constraints, state transitions, strategy bounds, and validation without network or database. Integration tests cover repositories, migrations, worker claiming/recovery, and API authorization with temporary infrastructure. Adapter contract tests use fakes and recorded/sanitized fixtures for provider mapping and error handling. Workflow tests exercise retries, quotas, review gates, and idempotency. Frontend tests focus on consequential review/control flows and correct display of failed or uncertain states.

Phase 1 tests validate Niche DNA schemas without a database and use a dedicated PostgreSQL `*_test` database for migration and API behavior. They cover account isolation, immutable revisions, stale updates, change events, authorization, and event cursor pagination. The database suite skips when `TEST_DATABASE_URL` is absent and refuses a database name without the `_test` suffix.

Build an end-to-end simulated cycle: fake trend → niche evaluation → idea/draft → media candidate → critique → approval gate → fake publication → fake metrics → bounded insight. Assert lineage and account isolation at each stage. External AI/API calls must be mockable; tests must never hold live publishing credentials or call a live publisher. Make `PUBLISHING_ENABLED=false` and the fake adapter the test defaults.

Run targeted suites for ordinary changes. Run broader integration and full-cycle suites when interfaces, lifecycle states, migrations, or safety gates change. Validate output schemas and prompt versions with fixtures and behavior checks, rather than tests that merely mirror prompt wording. Record any skipped external verification and the reason.
