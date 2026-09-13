# AGENTS.md

This repo is **vstack**: a collection of agent skills (Markdown) plus Python tooling to install and verify them. There is no application runtime; "the product" is the skill files and the manifest invariants around them.

## Commands

```bash
# Verify manifest/skill consistency (same check CI runs; exit 0 = clean)
python3 setup-vstack/scripts/verify.py
python3 setup-vstack/scripts/manage.py verify

# Full test suite (unittest only, no pytest; Python 3.11 in CI)
python3 -m unittest discover -s tests -v

# Eval suite only (Level 1 contracts + Level 2 trace invariants)
python3 -m unittest tests.eval.test_skill_contracts tests.eval.test_trace_invariants -v

# Preview what the installer would do (never mutates)
python3 setup-vstack/scripts/install.py --dry-run

# Check an arbitrary trace against W1-W7 invariants
python3 tests/eval/run_invariants.py tests/eval/fixtures/trace_w4_concurrency.json
```

## Layout

- `vmode/` and `setup-vstack/` are top-level skills; all other first-party skills live in `skills/<name>/`. Every skill folder needs `SKILL.md` **and** `README.md`.
- `setup-vstack/skills.json` is the single source of truth for the collection. Scripts in `setup-vstack/scripts/` manage it (`manage.py add/remove/set-source/set-required/list`).
- `vmode/` = workflow mode with `playbooks/` (feature, bug-fix, prototype, investigation, babysit) and `references/` (roles, triage).
- `tests/eval/` = deterministic evaluation harness for vmode (contracts, trace invariants, fixtures, LLM-gated probes). See `tests/eval/README.md`.
- `.claude-plugin/plugin.json` lists the local skills shipped as a Claude plugin. **Update it when adding or removing a local skill** (it is currently missing `skills/automate-me`).

## Invariants enforced by CI (easy to break unknowingly)

`verify.py` and `tests/eval/test_skill_contracts.py` fail on:

- Skill frontmatter `name` must equal the folder/manifest name; `description` must start with `Use when`.
- Every entry in `skills.json` needs `source` and `scope`; scope is `mine` or `external`, and `mine` requires source `vuon9/*` or `local`.
- Skills marked `required: true` in `skills.json` must exactly match the `## Required skills` bullet list in `vmode/SKILL.md` (parsed as `- \`name\`` lines). Change one, change the other.
- No em dashes (`—`) anywhere in `vmode/playbooks/`.
- No "narrating comment" placeholder patterns in fenced code blocks repo-wide (patterns are listed in `test_no_narrative_comment_placeholders_in_repo`).
- Role brief templates in vmode must keep their evidence clauses (raw evidence, `grep -n` citations, `gh pr checks`).

## Gotchas

- `manage.py` re-sorts `skills.json` by name and rewrites it with 2-space indent + trailing newline on every save; don't hand-edit ordering.
- Scripts under `setup-vstack/scripts/` import each other by bare module name (`from verify import ...`); run them from the repo root or as `python3 setup-vstack/scripts/<script>.py`. `pyrightconfig.json` adds `setup-vstack/scripts` to the path for type checking.
- Level 3 eval probes only call an LLM when `EVAL_LLM_API` and `EVAL_LLM_MODEL` env vars are set; without them they degrade to YES/SKIP/NEEDS-LLM. CI is intentionally 0% LLM, so keep tests deterministic and network-free.
- Eval fixtures in `tests/eval/fixtures/` were extracted from real runs; some intentionally encode violations (e.g. `trace_round1_feature.json` must fail W3). Don't "fix" them.
- Local planning docs (`docs/superpowers/`), `status-cache.json`, and `.pi/` are gitignored; keep specs/plans local unless asked to commit.

## CI & releases

- `validate.yml` (push/PR to main): `verify.py` + full unittest suite.
- `vmode-eval.yml` (PRs touching `vmode/**` or `tests/eval/**`): static contract/trace gates, then an advisory LLM semantic review (muse-spark).
- `vstack-synced-review.yml`: AI review on every PR event, converging to one comment per PR.
- Releases use release-please (`release.yml`, manual `workflow_dispatch`), so **commit messages must be Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`); scopes like `feat(eval):` and `fix(vmode):` are common in history.

## Writing skills

Follow the existing house style: `SKILL.md` with frontmatter (`name`, `description` starting with `Use when`), a companion `README.md`, and `references/` or `playbooks/` subdirs for anything loaded on demand. vmode's own SKILL.md is the model for progressive disclosure: wire existing skills instead of restating them.
