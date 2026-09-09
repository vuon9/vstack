### Investigation

**You own the answer. Plan, route, write.**

Use for understanding a thing: "how does X work", "why was Y built this way", "are we sure about Z". Read-only until you propose.

1. **Classify and anchor first.**
   Distinguish the question's core intent:
   - **Mechanism (`how`)**: runtime flow, architecture, call paths, boundary layers.
   - **Rationale (`why`)**: intent, history, design constraints, git blame, PR discussions.
   Anchor code before delegating: identify files, key symbols, and relevant commits via `git log` or `git blame`.
2. **Decompose and slice.**
   Assess complexity:
   - **Narrow / single-module**: dispatch a single `research` subagent (or trace in-session).
   - **Broad / cross-cutting**: decompose into 2-3 disjoint orthogonal slices (e.g. data model vs request flow vs config/infra). Dispatch `research` subagents concurrently.
3. **Calibrate evidence and epistemics.**
   Separate code-observable facts from inferences:
   - Facts must cite exact files with line ranges anchored via `grep -n` or read output.
   - For intent/rationale, cite commits, PRs, or docs; hedge when evidence is indirect ("appears to", "likely").
   - Reject unverified subagent claims; re-verify cited line spans yourself.
4. **Structured answer.**
   Present findings clearly:
   - **Overview**: the mental model and summary (who it is for, consumer/maintainer).
   - **How it works / Why it is this way**: step-by-step trace with anchored citations.
   - **Gotchas & edge cases**: non-obvious traps, expired states, or unhandled paths.
   - **Next action**: propose the minimal fix, design choice, or concrete next step if asked.