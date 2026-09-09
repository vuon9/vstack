# Roles & Subagents

Three model-agnostic capabilities reusable across harnesses and model providers. Each capability defines its operational role, capability profile, and structured prompt brief so any harness can dispatch it cleanly.

You own every subagent's work: review the diff, write your own summary, and never pass through unverified assertions.

---

## Harness Dispatch Protocol

When delegating tasks:

1. **Check available subagent tools in the runtime:**
   - **OpenCode**: Use the built-in `subagent` tool.
     - Never pass unregistered custom agent names (e.g. `agent: "watchdog"` will fail).
     - For `research`: Use `agent: "explore"` (read-only search and file reading) or `agent: "general"`.
     - For `general`: Use `agent: "general"` (read/write/shell tools enabled).
     - For `watchdog`: Use `agent: "general"` with background execution enabled (`background: true`).
   - **Pi (`@earendil-works/pi-coding-agent`)**:
     - Pi does not include a `subagent` tool by default.
     - If the `subagent` extension/tool is installed: Call `subagent` with `{ agent, task, cwd }` or `{ tasks: [...] }`.
     - Otherwise, dispatch via Pi's CLI in bash: `pi -p --no-session "<brief>"` (or `--model <model>` to match the parent session).
   - **Other harnesses / standalone**: If no subagent tool or CLI spawn exists, execute the task directly within the current session, preserving the role's boundary and verification standards.

2. **Self-contained prompt brief:**
   Always provide a complete, self-contained prompt to the subagent. Subagents launch in a fresh context window without prior chat history. Include:
   - Specific role and task objective.
   - Exact file paths and constraints.
   - Acceptance criteria or verification command.

---

## Role Specifications

### watchdog

- **Capability tier.** Light to medium reasoning with autonomous monitoring.
- **When.** A PR must reach green, or the user asks to babysit/monitor a PR.
- **Brief template:**
  ```markdown
  Role: watchdog
  Task: Drive PR <pr_number_or_url> to green.
  Instructions:
  1. Poll PR status and checks using `gh pr checks <pr>`.
  2. If conflicts occur, identify conflicting files and report or resolve if straightforward.
  3. If CI fails, inspect logs, identify the root failure, and apply minimal fixes.
  4. If review/bot comments are posted, triage per `references/triage.md`:
     - Fix valid bugs/security issues.
     - Dismiss false positives with concrete explanation.
     - Ask if high-risk or ambiguous.
  5. Stop and report as soon as all checks pass. Do not loop past green. Do not merge unless explicitly authorized.
  ```
  <!-- EDIT: pr-template -->

### general

- **Capability tier.** Mechanical worker or targeted implementer.
- **When.** Isolated, self-contained work that runs independently from the main thread.
- **Brief template:**
  ```markdown
  Role: general
  Task: <clear_task_summary>
  Target files: <comma_separated_paths>
  Invariants & Data Shapes: <key_boundaries>
  Verification: Run `<test_or_verification_command>` and ensure it passes.
  Return: Provide a summary of changes along with raw execution evidence: exact test/command output, passing assertion counts, and `git diff --stat`. Unsubstantiated claims will be rejected.
  ```

### research

- **Capability tier.** High context, read-only analytical reasoning.
- **When.** An investigation, architecture review, or understanding task.
- **Brief template:**
  ```markdown
  Role: research
  Task: Investigate <question_or_subsystem>.
  Focus areas: <specific_files_or_flows>
  Instructions:
  1. Trace code paths, dependencies, and execution flows using read/grep/glob.
  2. Identify ambiguities, design rationale, or regressions.
  3. Report findings with exact file and line citations. Before citing line spans, verify each symbol or line range using `grep -n` or read tool output. Return the raw grep or line output snippet as verification evidence.
  ```
