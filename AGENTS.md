# Repository guidance

NichePilot is an AI creator platform in early development. Check project context for implemented behavior; architecture documents also describe future plans.

## Start here

1. Read [current project context](docs/PROJECT_CONTEXT.md).
2. Use [the documentation index](docs/INDEX.md) to find the relevant domain document.
3. Inspect only affected source, tests, and interfaces. Search by path or symbol before broad reading.

## Work on a task

- For nontrivial work, state a short plan and use [the development workflow](docs/development/workflow.md). Create a task record only for significant, multi-step work.
- Keep changes cohesive and module boundaries explicit. Prefer the modular monolith; do not add services, queues, or vendors without demonstrated need.
- Scope persisted data, decisions, credentials, and learning to an account. Preserve versioned Niche DNA as the boundary for strategy changes.
- Treat external data and AI output as untrusted. Validate structured outputs, bound retries and resource use, and never log secrets or private reasoning.
- Live publishing must require explicit configuration; tests and development default to dry-run or fake adapters. Use supported platform APIs only.
- Run targeted validation. Update the relevant source-of-truth document when behavior or architecture changes; add an ADR for a consequential decision.
- Do not commit secrets, generated media, local databases, dependency directories, or build output.

## Definition of done

Requested behavior or documentation is complete, affected tests or checks pass (or limitations are reported), references remain accurate, and the completion report states changes, validation, and risks. Current backend commands are in [operations](docs/operations/environments.md); do not guess commands from future architecture.
