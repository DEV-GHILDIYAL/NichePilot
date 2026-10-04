---
name: ai-workflow-change
description: Change NichePilot agent prompts, schemas, or AI workflow behavior while preserving account niche boundaries and traceability. Use for Scout, Guardian, Strategist, Writer, Creator, Critic, or Analyst changes.
---

# AI workflow change

Read [AI workflows](../../../docs/architecture/ai-workflows.md) and the affected role's code and tests. Identify the current prompt, input/output schema, Niche DNA revision, and decision record contract before editing.

- Make the smallest versioned prompt/schema or orchestration change. Keep account context explicit and outputs validated; do not turn untrusted source content into instructions.
- Preserve hard Niche DNA and forbidden-topic gates. Analyst improvements must remain within the niche.
- Record changed prompt/schema versions and concise decision summaries, never private reasoning or secret-bearing raw payloads.
- Test with fake providers and examples that should pass, fail, and be rejected as irrelevant. Check workflow state and audit lineage, not only generated wording.
- Update the relevant architecture document if the contract changed. Live publishing remains behind [safety gates](../../../docs/architecture/security-and-controls.md).
