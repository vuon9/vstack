#!/usr/bin/env python3
"""Install skills from skills.json from their upstream sources.

Idempotent: rerunning it refreshes git-sourced skills. If a skill is already
installed from a different source, it is removed first so the new source wins.

Scopes:
  --mine       skills written by vuong (scope: mine)
  --external   skills from other authors (scope: external)
  --required   the skills vmode needs (required: true)
  --all        everything (default)
"""

import argparse
import json
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(SKILL_DIR, "skills.json")
LOCK_PATH = os.path.expanduser("~/.agents/.skill-lock.json")


def load_skills():
    try:
        with open(MANIFEST) as fh:
            return json.load(fh)["skills"]
    except (OSError, ValueError, KeyError) as exc:
        raise RuntimeError(f"could not load {MANIFEST}: {exc}") from exc


def current_source(name):
    try:
        with open(LOCK_PATH) as fh:
            lock = json.load(fh).get("skills", {})
    except Exception:
        lock = {}
    entry = lock.get(name) or {}
    return entry.get("source") or entry.get("sourceType") or None


def filter_skills(skills, scope):
    if scope == "mine":
        return [s for s in skills if s.get("scope") == "mine"]
    if scope == "external":
        return [s for s in skills if s.get("scope") != "mine"]
    if scope == "required":
        return [s for s in skills if s.get("required")]
    return skills  # all


def parse_args():
    parser = argparse.ArgumentParser(description="Install skills from skills.json.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--mine", action="store_true", help="install vuong-written skills only"
    )
    group.add_argument(
        "--external", action="store_true", help="install other authors' skills only"
    )
    group.add_argument(
        "--required",
        action="store_true",
        help="install only the skills vmode requires",
    )
    group.add_argument(
        "--all", action="store_true", help="install everything (default)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print actions without running external installation commands",
    )
    return parser.parse_args()


def run_or_dry(cmd, dry_run):
    """Run cmd, or print it when dry_run is set.

    Returns (exit_code, error_text) where error_text is the captured
    stderr/stdout on a real failure and an empty string otherwise.
    """
    if dry_run:
        print(f"[dry-run] would run: {' '.join(cmd)}")
        return 0, ""
    res = subprocess.run(cmd, check=False, capture_output=True)
    if res.returncode == 0:
        return 0, ""
    err = (res.stderr or res.stdout or b"").decode(errors="replace").strip()
    return res.returncode, err


def main():
    args = parse_args()
    scope = "all"
    if args.mine:
        scope = "mine"
    elif args.external:
        scope = "external"
    elif args.required:
        scope = "required"

    skills = filter_skills(load_skills(), scope)
    print(f"scope: {scope}  |  entries: {len(skills)}")

    ok, failed = [], []
    dry_run = args.dry_run

    for entry in skills:
        name = entry["name"]
        source = entry.get("source")

        if source in (None, "", "local"):
            print(
                f"[skip] {name}: local/manual ({entry.get('note', 'no repo source')})"
            )
            continue

        existing = current_source(name)
        if existing and existing != source and existing != "local":
            print(
                f"[swap] {name}: removing existing ({existing}) before installing from {source}"
            )
            run_or_dry(
                ["npx", "-y", "skills", "remove", name, "-g", "-y"],
                dry_run,
            )

        print(f"[install] {name} <- {source}")
        exit_code, err = run_or_dry(
            [
                "npx",
                "-y",
                "skills",
                "add",
                "-g",
                source,
                "--skill",
                name,
                "--full-depth",
                "-y",
            ],
            dry_run,
        )
        if exit_code == 0:
            ok.append(name)
        else:
            failed.append((name, err))
            print(f"[FAILED] {name}:\n{err}")

    print()
    print(f"Installed/refreshed: {len(ok)}  |  Failed: {len(failed)}")
    for name, err in failed:
        print(f"  - {name}: {err[:200]}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
