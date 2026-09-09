# vmode

A manual development-workflow mode that encodes Vuong's preferred way of
building software. Model-agnostic and stack-agnostic.

## Use it with a prompt

Say what you want in plain words. Prompts come first; the scripts below are
only the fallback.

- "Work in vmode" -> activates `/vmode`. vmode checks its required skills; if
  any is missing, it runs `set-it-up --required`.
- "How does the auth flow work?" -> investigation playbook with the `research`
  role. Returns a cited answer, not a summary.
- "Why was this table added?" -> investigation. Ends in a cited answer or a
  proposed fix.
- "Build the export feature" -> implementation playbook. Clear scope goes
  through `brainstorming`; foggy or big scope goes through `wayfinder`.
- "Babysit PR #123 until it's green" -> the `watchdog` role. It drives the PR
  to green, then stops and reports.
- "Handle this small thing separately" -> the `general` role with a clear,
  self-contained brief.

## What happens on /vmode

1. vmode checks its required skills. Missing one? It runs
   `set-it-up --required` first.
2. It reads the Principles in full, then the matched playbook (`feature`, `bug-fix`, `prototype`, `investigation`, or `babysit`).
3. It copies the playbook steps into the todolist verbatim. A skipped step
   stays with `skip: <reason>`.

## Roles

- **watchdog** drives a PR to green, triages review/bot comments, then stops and reports.
- **general** handles isolated work with a clear brief.
- **research** builds the picture and returns a cited report.

Full details live in `references/roles.md`.

## Subagent Dispatch & Harness Compatibility

vmode delegates subagent tasks through prompt instructions and role briefs rather than hardcoded proprietary model IDs:

- **OpenCode**: Native built-in `subagent` tool (`general` and `explore` built-in, or custom profiles in `.opencode/agents/`).
- **Pi (`@earendil-works/pi-coding-agent`)**: Invokes subagents via Pi's `subagent` extension or prompt instructions.
- Subagents receive capability-tiered briefs (`general`, `research`, `watchdog`) so the user's configured model or parent harness executes them cleanly.

## Why the rules live in two layers

vmode learns from `poteto-mode` (from `cursor/plugins/pstack`): triggers and principles. Instead of coupling to specific Cursor features or fixed commercial models, vmode distills the core mechanics:

- **Triggers** (Non-negotiables) are moment-of-recognition routing. The agent
  scans them while working; the moment a situation appears, the matching line
  fires.
- **Principles** are read-first grounding. The opener forces the agent to read
  them in full at the start, and the reply rule says to name each principle
  that shaped a decision. A rule must exist as a principle, or the citation
  rule can't reference it.

That's why a rule like "keep generated docs local" appears twice: once as a
trigger (fires at the moment) and once as a principle (the standing rule read
up front and cited). If you change such a rule, edit both places.

## Scripts (additional)

Only needed when you want the underlying commands directly.

- `python3 set-it-up/scripts/install.py --all` installs everything.
- `python3 set-it-up/scripts/install.py --required` installs just what
  vmode needs.
- `npx skills update -g` refreshes installed skills to latest.

## Making it yours

Fork the repo and edit only the marked spots:

- The behavior-test step in `playbooks/feature.md`.
- The PR template reference in `references/roles.md`.

Everything else is style, not stack.
