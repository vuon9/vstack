# VStack

A modular collection of skills and workflows for AI coding agents, designed to be harness- and model-agnostic.

The workflow system in `vmode` is inspired by the trigger-and-principle architecture of `poteto-mode` (from [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)), refined into an editor-agnostic, lightweight form without vendor lock-in, proprietary model couplings, or complex external dependencies.

## Prerequisites

- **Python 3.10+** (Python 3.11 recommended). Used for collection verification (`set-it-up/scripts/verify.py`), installation tooling, and evaluation test suites.
- **Node.js & npx** (Node 18+). Required to run `npx skills add` for installing skills into your agent environments.
- **Hunk** (`hunk-review` skill). Used for interactive local diff reviews before opening pull requests. See [modem-dev/hunk](https://github.com/modem-dev/hunk).
- **Cua Driver** (`cua-driver` skill). Optional runtime dependency for native desktop GUI automation on macOS, Windows, and Linux. See [trycua/cua](https://github.com/trycua/cua).
- **GitHub CLI** (`gh`). Required for PR watchdog automation, checks polling, and issue publishing.

## Install

Install this repository with the open agent skills CLI:

```bash
npx skills add -g vuon9/vstack
```

The `skills` tool opens an interactive flow where you can choose which skills
and agents to install. The collection is managed and refreshed by
[set-it-up](./set-it-up/SKILL.md) (`skills.json` is the
single source of truth for what gets installed).

## Verify

A deterministic check validates the collection: every `skills.json` entry,
the `## Required skills` list in [vmode](./vmode/SKILL.md), and the
repo-local skills agree (name, source, scope, description, README).

```bash
python3 set-it-up/scripts/manage.py verify    # exit 0 when clean
python3 set-it-up/scripts/install.py --dry-run # preview install actions
```

CI runs the same verification plus the unit test suite on every push and PR
(`.github/workflows/validate.yml`).

## Approaches

- Free to install: Using the first command you see in the **Install** part to choose skills and install whatever you wanted
- Wanted to try `vmode`: It's my preferred way to start working on things, install `vmode` and read its README to having more context

## Skills

### Written by me

- [vmode](./vmode/SKILL.md). The manual development-workflow mode (behavior-first, review and PR discipline, watchdog/general/research roles)
- [set-it-up](./set-it-up/SKILL.md). Install and refresh this collection from `skills.json`
- [automate-me](./skills/automate-me/SKILL.md). Capture personal working conventions and preferences into an agent `-mode` skill
- [shipping-darwin-apps](./skills/shipping-darwin-apps/SKILL.md). Build and ship iOS/macOS apps (signing, notarization, TestFlight, DMG)
- [gh-workflows](https://github.com/vuon9/gh-workflows). Reusable GitHub Actions workflows

### Copied from cursor/plugins, adjusted for editor-agnostic use

- [bro](./skills/bro/SKILL.md). Restate the last message in plain language (as-is)
- [code-teach](./skills/code-teach/SKILL.md). Explain a body of work, cursor's `teach` renamed (as-is)
- [how](./skills/how/SKILL.md). Explain how a subsystem works (edited: Cursor-specific wording normalized)
- [unslop](./skills/unslop/SKILL.md). Remove AI tells from writing (as-is)
- [why](./skills/why/SKILL.md). Explain why a change (edited: Cursor-specific wording normalized)

### From other authors, installed from their repos

- [mattpocock/skills](https://github.com/mattpocock/skills)
  - diagnosing-bugs
  - grill-me
  - grill-with-docs
  - grilling
  - handoff
  - prototype
  - teach
  - to-prd
  - to-spec
  - wayfinder
- [obra/superpowers](https://github.com/obra/superpowers)
  - brainstorming
  - dispatching-parallel-agents
  - executing-plans
  - receiving-code-review
  - requesting-code-review
  - subagent-driven-development
  - systematic-debugging
  - test-driven-development
  - verification-before-completion
  - writing-plans
  - writing-skills
- [emilkowalski/skills](https://github.com/emilkowalski/skills)
  - apple-design
- [vercel-labs/skills](https://github.com/vercel-labs/skills)
  - find-skills
- [trycua/cua](https://github.com/trycua/cua)
  - cua-driver
- [modem-dev/hunk](https://github.com/modem-dev/hunk)
  - hunk-review

Each skill folder includes a `README.md` with human-facing use cases. `SKILL.md`
stays focused on instructions that agents should load at runtime.

## License

MIT
