#!/usr/bin/env python3
"""Manage the skills.json manifest.

Commands:
  list                          Show current skills (name, source, scope, required).
  add <name> --source <repo>    Add a favorite, or change its source if it exists.
    [--scope mine|external] [--required]
  remove <name>                 Remove a favorite from the manifest.
  set-source <name> <repo>      Change only the source of an existing favorite.
  set-required <name> <true|false>  Mark a favorite as required by vmode or not.

After any change, run scripts/install.py to apply it to the local machine.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from verify import verify_manifest

MANIFEST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "skills.json"
)


def load():
    try:
        with open(MANIFEST) as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"could not load {MANIFEST}: {exc}") from exc
    if "skills" not in data:
        data["skills"] = []
    return data


def save(data):
    data["skills"].sort(key=lambda s: s["name"])
    try:
        with open(MANIFEST, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
    except OSError as exc:
        raise RuntimeError(f"could not write {MANIFEST}: {exc}") from exc


def find(entries, name):
    for entry in entries:
        if entry["name"] == name:
            return entry
    return None


def cmd_list(data):
    for entry in sorted(data["skills"], key=lambda s: s["name"]):
        source = entry.get("source", "?")
        scope = entry.get("scope", "external")
        required = "required" if entry.get("required") else ""
        suffix = (
            f"  ({entry['note']})" if source == "local" and entry.get("note") else ""
        )
        print(f"{entry['name']}\t{source}\t{scope}\t{required}{suffix}")


def cmd_add(data, name, source, scope, required):
    entry = find(data["skills"], name)
    if entry:
        entry["source"] = source
        entry.pop("note", None)
        print(f"updated {name} -> {source}")
    else:
        entry = {"name": name, "source": source}
        data["skills"].append(entry)
        print(f"added {name} <- {source}")
    if scope:
        entry["scope"] = scope
    if required:
        entry["required"] = True


def cmd_remove(data, name):
    before = len(data["skills"])
    data["skills"] = [e for e in data["skills"] if e["name"] != name]
    print(f"removed {name}" if len(data["skills"]) < before else f"not found: {name}")


def cmd_set_source(data, name, source):
    entry = find(data["skills"], name)
    if not entry:
        print(f"not found: {name}", file=sys.stderr)
        sys.exit(1)
    entry["source"] = source
    entry.pop("note", None)
    print(f"{name} -> {source}")


def cmd_set_required(data, name, value):
    entry = find(data["skills"], name)
    if not entry:
        print(f"not found: {name}", file=sys.stderr)
        sys.exit(1)
    entry["required"] = value
    print(f"{name} required={value}")


def main():
    parser = argparse.ArgumentParser(description="Manage skills.json.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")
    sub.add_parser("verify")

    p_add = sub.add_parser("add")
    p_add.add_argument("name")
    p_add.add_argument("--source", required=True)
    p_add.add_argument("--scope", choices=["mine", "external"])
    p_add.add_argument("--required", action="store_true")

    p_rm = sub.add_parser("remove")
    p_rm.add_argument("name")

    p_set = sub.add_parser("set-source")
    p_set.add_argument("name")
    p_set.add_argument("source")

    p_req = sub.add_parser("set-required")
    p_req.add_argument("name")
    p_req.add_argument("value", type=lambda v: v.lower() in ("true", "1", "yes"))

    args = parser.parse_args()

    if args.command == "verify":
        repo_root = Path(__file__).resolve().parent.parent.parent
        errors = verify_manifest(repo_root)
        if errors:
            for err in errors:
                print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(1)
        print("Verification passed.")
        return

    data = load()

    if args.command == "list":
        cmd_list(data)
        return
    if args.command == "add":
        cmd_add(data, args.name, args.source, args.scope, args.required)
    elif args.command == "remove":
        cmd_remove(data, args.name)
    elif args.command == "set-source":
        cmd_set_source(data, args.name, args.source)
    elif args.command == "set-required":
        cmd_set_required(data, args.name, args.value)

    save(data)


if __name__ == "__main__":
    main()
