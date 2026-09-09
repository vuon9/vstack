---
name: automate-me
description: "Use when capturing personal working conventions into an agent mode skill, or when running 'automate me', 'create/update/refresh my -mode skill', or wanting agents to adapt to how the user works. Drafts or revises a personal -mode skill via writing-skills and unslop, pulling fresh evidence from transcripts or structured grilling."
disable-model-invocation: true
---

# Automate me

A guided flow for turning an engineer's working conventions into an agent mode skill. The output is one `-mode` skill tailored to them (such as `vmode`, `alex-mode`, or `priya-mode`).

This skill orchestrates evidence mining, skill drafting via `writing-skills`, and prose hardening via `unslop`.

## Flow

### 0. Check for an existing skill

Identify the user's handle (e.g. from git config `user.name` or conversation). Look for an existing mode skill:

- In active skill stores: `~/.agents/skills/<handle>-mode/SKILL.md` or `~/.agents/skills/vmode/SKILL.md`
- In project-local skills: `skills/<handle>-mode/SKILL.md` or `.agents/skills/<handle>-mode/SKILL.md`
- In harness-specific locations: `.cursor/skills/*-mode/SKILL.md`, `.opencode/skills/*-mode/SKILL.md`

If an existing mode skill is found, ask whether to update it or start fresh:
- **Update (default)**: Mine history strictly since the skill was last modified. Preserve established rules the user has not contradicted.
- **Fresh**: Start from scratch.

### 1. Mine working preferences & history

Gather behavioral signals across two tracks:

#### A. Multi-harness transcript mining
Locate session logs without crossing unrelated project boundaries:
- **OpenCode**: `~/.config/opencode/` or active workspace session logs.
- **Pi**: `~/.pi/agent/sessions/` within the active working tree scope.
- **Cursor**: Workspace-scoped transcripts if present.

Pre-filter user turns for constraint cues to avoid token bloat:
`grep -Ei "(don't|never|always|stop doing|prefer|shorter|too verbose|run tests first|no comments|verify)"`

Look for 6 signal categories:
1. **Reply style**: length, terseness, formatting, tone, banned punctuation (e.g. em dashes, connector colons).
2. **Autonomy line**: when to ask vs when to proceed, irreversible vs reversible actions.
3. **Verification posture**: how "done" is proven, unit vs end-to-end vs real artifact execution.
4. **Subagent habits**: when to delegate, model preferences, serial vs parallel dispatch.
5. **Code & comment discipline**: clean code rules, comment policies (e.g. why-only, no narrating comments).
6. **Tooling & workflow gates**: worktrees, test runners, linters, review gates.

#### B. Git commit & review history
Inspect recent commits and PR discussions authored by the user:
```bash
git log --author="$(git config user.name)" -n 25 --oneline
```
Identify conventions in commit messages, review feedback given to others, and PR descriptions.

### 2. Structured clarification (the interview)

Mining alone misses latent intent. Use structured multiple-choice questions to confirm findings:
1. Ask 2-3 focused questions covering ambiguous areas (autonomy, verification requirements, reply length).
2. Allow selecting multiple items.
3. Follow with one free-form prompt catching edge cases.

### 3. Choose architecture & draft

Mode skills follow an adaptive architecture:
- **Single-file (standard)**: For compact, straightforward conventions. Combines triggers, non-negotiables, principles, and reply rules into one `SKILL.md`.
- **Modular (complex workflows)**: For multi-track development modes (like `vmode`). Scaffolds `SKILL.md` + `playbooks/` (e.g. `feature.md`, `bug-fix.md`) + `references/roles.md`.

Drafting rules (via `writing-skills` principles):
- Name the mode `<handle>-mode` (or `<handle>`).
- Set frontmatter `disable-model-invocation: true` so the heavy mode only fires on explicit user intent (`/<handle>-mode` or direct request).
- Write triggers as moment-of-recognition lines.
- Write principles as standing grounding rules.
- Ground rules in concrete observable constraints, not vague aspirations.

### 4. Polish with unslop

Run the entire draft through `unslop`:
- Ban buzzwords, sycophancy, and puffery.
- Remove em dashes and connector colons.
- Enforce short, active declarative sentences.
- Ensure the agent speaks plainly and directly.

### 5. Review and save

Ask the user where to place the generated mode:
- **Global (default)**: `~/.agents/skills/<handle>-mode/` (active across all sessions).
- **Project repository**: `skills/<handle>-mode/` or `.agents/skills/<handle>-mode/`.

Show the draft diff to the user. Once approved, write the files and verify them.

## Guardrails

- **No single-instance overfitting**: Do not convert a one-off remark into a permanent non-negotiable. Require multiple transcript occurrences or direct user confirmation.
- **Reference existing skills, do not duplicate**: Reference tools like `test-driven-development` or `hunk-review` by name. Do not copy their instructions into the mode skill.
- **Operational over poetic**: A mode skill is an execution contract for an AI agent, not personal prose. Keep every rule actionable.
