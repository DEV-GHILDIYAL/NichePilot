# Development workflow

For a nontrivial task: clarify the requested behavior and affected boundary; read root `AGENTS.md`, [project context](../PROJECT_CONTEXT.md), and [index](../INDEX.md); open the relevant document and only then inspect targeted code and tests. State a short plan, implement the smallest coherent change, run targeted tests/lint/type checks, and broaden validation only for a concrete integration risk. Update current documentation if behavior or architecture changed; add an [ADR](../adr/README.md) for a consequential decision. Report changes, validation, and limits.

Use [task records](../tasks/README.md) for significant multi-step work that may span sessions; do not make a record for a small edit. Keep each record short and link affected documents. A completed record is history, not mandatory context. The index and project context are navigation/current state, not a task log.

Git changes should be small and coherent with clear messages. Commit migrations with the corresponding model change once schema work begins. Never commit secrets, generated media, local data, or vendored dependencies. Do not perform remote Git operations without an explicit request.
