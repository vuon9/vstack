---
name: set-it-up
description: Use when restoring or updating the global skill set, installing vmode's required skills, adding, removing, or changing the source of a favorite, or checking what is installed. Installs, refreshes, and catalogs Vuong's agent skills (written + preferred from other authors) using skills.json (a repo + skill-name manifest with scope and required flags) and wrapper scripts.
---

# Set It Up

Catalog Vuong's skills in `skills.json` (each entry has a `source` repo and a `name`, plus `scope` and `required`), then install or refresh them. This keeps a single, versioned list of every skill that matters instead of relying on the installed state alone.

## Files

- `skills.json`. The manifest. Entries carry `name`, `source`, `scope` (mine/external), and an optional `required` flag for vmode.
- `scripts/manage.py`. List, add, remove, change source, mark required.
- `scripts/install.py`. Installs or refreshes entries, filtered by scope. Idempotent.
- `scripts/update.py`. Runs `npx skills update -g` to refresh installed git-sourced skills.
- `scripts/sync_cursor.py`. Refreshes the vendored cursor skills (`code-teach`, `bro`, `unslop`).

## Scopes

- `mine`. Skills written by Vuong (source `vuon9/*`).
- `external`. Preferred skills from other authors.
- `required`. The skills the `vmode` mode needs to work (a mix of mine and external).

## Install

```bash
python3 scripts/install.py --all        # everything (default)
python3 scripts/install.py --mine       # Vuong-written skills only
python3 scripts/install.py --external   # other authors' skills only
python3 scripts/install.py --required   # exactly what vmode needs
```

`vmode` checks its required skills on start. If any is missing, it routes here with `--required`.

## Vendored cursor skills

`code-teach`, `bro`, `how`, `unslop`, and `why` are vendored copies of cursor/plugins' skills. `code-teach` (cursor's `teach`) is renamed; `how` and `why` are edited to normalize Cursor-specific wording ("the Cursor environment", "`mcps/` directory Cursor exposes", "Ask mode", "agent mode") so they work across editors. `bro` and `unslop` needed no edits (they were already editor-agnostic).

- `code-teach`, `bro`, and `unslop` are unmodified apart from renames, so `scripts/sync_cursor.py` refreshes them from upstream safely.
- `how` and `why` are edited. Do not re-clone them blindly from cursor; refresh manually and re-apply the normalization.

```bash
python3 scripts/sync_cursor.py    # refresh code-teach, bro, unslop
```

## Manifest format

```json
{
  "skills": [
    { "name": "gh-workflows", "source": "vuon9/gh-workflows", "scope": "mine" },
    { "name": "brainstorming", "source": "obra/superpowers", "scope": "external", "required": true },
    { "name": "cua-driver", "source": "https://github.com/trycua/cua/tree/main/libs/cua-driver/rust/Skills/cua-driver", "scope": "external" }
  ]
}
```

- `name`. The skill name (must match the `name:` in its `SKILL.md`).
- `source`. An `owner/repo` GitHub source, a full GitHub tree URL pointing at a nested skill, or `local` for a manually-managed skill that has no repo source.
- `scope`. `mine` (Vuong-written) or `external` (other authors).
- `required`. Optional `true` for skills the `vmode` mode depends on.
- `note`. Optional; only used for `local` entries.

## Manage the list

Use `scripts/manage.py` to edit the manifest deterministically instead of hand-editing JSON:

```bash
# see what's listed (name, source, scope, required)
python3 scripts/manage.py list

# add a favorite (or change its source if it already exists)
python3 scripts/manage.py add <name> --source <owner/repo> [--scope mine|external] [--required]

# remove a favorite (stops it being (re)installed)
python3 scripts/manage.py remove <name>

# change only the source of an existing favorite
python3 scripts/manage.py set-source <name> <owner/repo>

# mark a favorite as required by vmode (or not)
python3 scripts/manage.py set-required <name> true
```

Notes:

- `add` on an existing name updates its source (that is the "remove the old and add" swap).
- Removing from the manifest only prevents future installs. To remove the copy already on the machine, run `npx skills remove <name> -g -y`.
- Edits are sorted by name on save, keeping the file readable.

## How it behaves

- Every `source != "local"` entry is installed from its upstream repo, so it stays updateable.
- If a skill is installed from a **different** source than the manifest, `install.py` removes the old one first so the manifest source wins.
- `local` entries are skipped.
- `--full-depth` is always passed to `npx skills add` so nested skills (for example `cursor/plugins` under `pstack/skills/`) are found.

## Notes

- The manifest is the single source of truth for the desired set, not the global install state. Regenerate it from `npx skills list -g` (or `~/.agents/.skill-lock.json`) when the collection changes.
- After adding a skill here, also add it to `.claude-plugin/plugin.json` and the collection `README.md` to keep it grouped and documented.
- If a skill already exists locally but was not installed from a repo, the first install adopts or overwrites it; `npx skills remove <name> -g -y` first if you want a clean start.
