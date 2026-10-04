# Documentation index

Read [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) first. Open only documents related to the task; architecture pages distinguish current contracts from future plans.

- System boundaries and future repository modules → [system](architecture/system.md)
- Entities, ownership, and lifecycles → [domain model](architecture/domain-model.md)
- Agent roles, prompts, and learning → [AI workflows](architecture/ai-workflows.md)
- Images, audio, subtitles, video, and storage → [media pipeline](architecture/media-pipeline.md)
- Dashboard navigation and user journeys → [dashboard](architecture/dashboard.md)
- Trend, AI, storage, and publishing adapters → [integrations](architecture/integrations.md)
- Runs, decisions, logs, usage, and health → [observability](architecture/observability.md)
- Safety, credentials, and publication controls → [security and controls](architecture/security-and-controls.md)
- Task steps and task records → [development workflow](development/workflow.md), [task convention](tasks/README.md)
- Test levels and side-effect-free cycle → [testing](development/testing.md)
- Phase order and milestones → [roadmap](development/roadmap.md)
- Environments and configuration → [operations](operations/environments.md)
- Why major choices were made → [ADR index](adr/README.md)

Reusable procedures for specialized changes live in [repository skills](../.codex/skills/). They supplement the documents above; they are not general reading.
