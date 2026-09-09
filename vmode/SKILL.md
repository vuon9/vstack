---
name: vmode
description: "Use when developing software in vmode: Vuong's preferred workflow for any kind of software, a manual mode triggered with /vmode. Behavior-first proof, minimal long-term fixes, review and PR discipline, implementation and investigation tracks, and model-agnostic subagent roles (watchdog, general, research)."
disable-model-invocation: true
---

# vmode

A manual mode for building software the way Vuong would. It wires existing skills instead of restating them, and stays model-agnostic so it works with any model or harness.

## Non-negotiables

Start every task by checking the required skills are available (confirming presence in the active skills manifest or checking that `<skill>/SKILL.md` exists and is non-empty; if any is missing, run `set-it-up --required`), then reading the Principles below in full, and the matched playbook, before doing anything else. Then copy the matched playbook's steps into your todolist verbatim. A step you skip stays in the list with `skip: <reason>`. In your reply, name each principle that shaped a decision and the specific choice it changed. A citation with no decision behind it means the principle was skipped.

Remaining triggers.

- New feature or behavior change -> read `playbooks/feature.md`.
- Bug, defect, or unexpected regression -> read `playbooks/bug-fix.md`.
- Empirical fork, visual design, or throwaway layout -> read `playbooks/prototype.md`.
- Understanding a thing, or "how or why does this work" -> read `playbooks/investigation.md` (leverages `how` and `why` patterns) and use the `research` role.
- PR babysitting, CI green, or review feedback -> read `playbooks/babysit.md` and consult `references/triage.md`.
- Scoped unit or functional change -> use `test-driven-development`.
- Before asking the user a "which approach" fork -> check whether the answer is observable, then probe; reserve the ask for a preference call.
- A pattern that keeps repeating -> suggest distilling it into a small skill; ask the user first.
- Writing any prose, PR, commit, or doc -> run `unslop`. Your reply is a prose surface.
- Local review work -> use `hunk-review`.
- Reviewing a PR or task -> use `requesting-code-review` then `receiving-code-review`. Confirm the report before posting to GitHub.
- A PR needs to reach green -> use the `watchdog` role. It stops and reports once green, never loops past green.
- Anything isolated from the main thread -> use the `general` role with a clear brief.
- About to declare done -> verify against the real artifact, not "it compiles".
- Planning or brainstorming produced a spec or plan doc -> keep it local. Do not commit it to the remote origin unless the user asks.

## Required skills

vmode depends on these. Verify their availability when vmode starts by checking their manifest presence or `<skill>/SKILL.md` file existence. If any is missing or unreadable, run `set-it-up --required`.

- `brainstorming`
- `wayfinder`
- `test-driven-development`
- `unslop`
- `hunk-review`
- `requesting-code-review`
- `receiving-code-review`

Its own roles, playbooks, and references ship inside vmode.

## Principles

Each principle names when it applies. Read it before acting on that situation.

- **Behavior first.** When a feature is user-facing. Prove the behavior with behavior/feature tests (BDD), not just that functions pass.
- **TDD for scope.** When the change is scoped or non-behavioral. Write the unit test first via `test-driven-development`.
- **Reproduce before fixing.** When addressing any defect. Create an observable repro before writing code.
- **Minimal, and long-term.** When sizing a change, or tempted to stack a "quick fix". Smallest change that truly solves it, and prefer a real long-term fix.
- **Verify, don't assume.** When about to declare done. Prove it against the real artifact, not "it compiles". Require raw evidence, not claims.
- **The ask is the slow path.** Before asking the user a fork. Check whether the answer is observable, then probe; reserve the ask for a preference call.
- **Confirm before posting.** When a review or comment goes to GitHub. Check the report is sound first.
- **Triage before churning.** When handling review or bot comments. Classify into fix, dismiss with proof, or ask.
- **Keep generated docs local.** When planning or brainstorming produced a spec, plan, or similar doc. Keep it local; commit to the remote origin only when the user asks.
- **PR template.** When opening a PR. Follow the repo or org template.
- **Babysit, then stop.** When a PR needs to reach green. Drive it there, then stop and report. Never loop past green.
- **Delegate what is isolated.** When work is unrelated to the main thread. Send it to a subagent with a clear, self-contained brief.
- **Autonomy line.** Always. Proceed on reversible work, pause for irreversible writes. Candor over agreement, and "no" is valid.
- **Principles trace to a decision.** In every reply. Name a principle only when it changed a concrete choice.

## Writing the reply

Write the reply clean as you draft it. The cleanup-afterward pass fails, so never generate the bad sentence in the first place.

- **Short declarative sentences.** One thought per sentence, ended with a period.
- **No long dash.** The em dash is banned outright. Use a period or a comma.
- **No colon as a connector.** A colon before a list is fine; a colon joining two clauses mid-sentence is out.
- **Terse is not an excuse to drop content.** Short sentences, but keep the details, tradeoffs, choices, and open decisions.
- **Name who the work is for first.** The consumer and the maintainer, before any implementation detail. If you can't say what either would notice, the work or the explanation is off.
- **Never fabricate a link or citation.** Link only artifacts you produced or read in this session.

## Comments

Comments follow the same rule as the reply. Write them clean as you go. A flat "no narrating comments" ban doesn't catch them; you have to not write them in the first place.

- **No narrating comments.** A `// Phase 1: add cards` line above a block is out. The assertion or log string is the only doc you need.
- **Say it in the assertion.** Write `assert(ok, 'persisted across restart')`, not a `// move the card` comment plus the code.
- **Keep a comment only for a non-obvious why.** If the code can't show the reason, comment it. Otherwise don't.
- **Applies everywhere.** Every file you produce, including subagent diffs and verify scripts.

## Roles & Subagents

Three model-agnostic capabilities. When delegating, invoke the subagent mechanism available in the host harness (such as OpenCode's `subagent` tool, Pi's `subagent` tool/extension, or background process dispatch) using the role's prompt brief.

- **watchdog** drives a PR to green, triages reviews, then stops with a report.
- **general** handles isolated work with a clear brief.
- **research** builds the picture for an investigation and returns a cited report.

Read `references/roles.md` for role specifications and dispatch instructions. You own every subagent's work: review its diff, write your own summary, and never pass through unverified assertions.

## Adapt me

Edit only these spots to fit your stack and tools. Everything else is style, not stack.

- The behavior-test step in `playbooks/feature.md`. Marker `<!-- EDIT: behavior-test -->`.
- The PR template reference in `references/roles.md`. Marker `<!-- EDIT: pr-template -->`.
- The description above, to name the person or project.
