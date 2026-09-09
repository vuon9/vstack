# Set It Up

Catalog and reinstall Vuong's agent skills (written + preferred from other
authors) via a single manifest (`skills.json`).

## Use it with a prompt

Say what you want in plain words. Prompts come first; the scripts below are
only the fallback.

- "Install all my skills" -> `python3 scripts/install.py --all`
- "Install what vmode needs" -> `python3 scripts/install.py --required`
- "Install only my own skills" -> `python3 scripts/install.py --mine`
- "Check the collection is consistent" -> `python3 scripts/manage.py verify`
- "Add the skill 'foo' from 'bar/repo'" -> `python3 scripts/manage.py add foo --source bar/repo`
- "Add 'foo' as mine and required by vmode" -> `python3 scripts/manage.py add foo --source bar/repo --scope mine --required`
- "Remove 'foo'" -> `python3 scripts/manage.py remove foo`
- "Refresh everything to latest" -> `npx skills update -g`

## Scripts (additional)

Only needed when you want the underlying commands directly.

- `python3 scripts/manage.py`. List, add, remove, change source, mark required,
  verify.
- `python3 scripts/manage.py verify`. Check `skills.json`, the vmode
  required list, and repo-local skills agree. Exits 0 when clean.
- `python3 scripts/install.py`. Install/refresh. Filters: `--mine`, `--external`,
  `--required`, `--all` (default).
- `python3 scripts/install.py --dry-run`. Print the install/remove actions
  without running them.
- `python3 scripts/update.py`. Refresh installed git-sourced skills to latest.
- `python3 scripts/sync_cursor.py`. Refresh the vendored cursor skills
  (`code-teach`, `bro`, `unslop`).

## Why

Rather than relying on the installed global state, this keeps one versioned
list of the skills you care about, each pinned to its `owner/repo` source so it
stays updateable with `npx skills update`. The `vmode` mode checks its required
skills and routes here when something is missing.

## Notes

- `python3 scripts/manage.py add <name> --source <repo> --scope mine` adds a
  favorite (or changes its source). `--required` marks it as needed by `vmode`.
- After any change, run `python3 scripts/install.py` to apply it locally.
- Some skills are local-only and listed with `"source": "local"`. They are
  skipped by the installer and must be kept manually.
