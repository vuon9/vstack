#!/usr/bin/env python3
"""Deterministic verification of skills.json, vmode required list, and skill files."""

import json
import re
import sys
from pathlib import Path


def parse_vmode_required(vmode_skill_path: Path) -> set[str]:
    if not vmode_skill_path.is_file():
        raise FileNotFoundError(f"Missing {vmode_skill_path}")

    text = vmode_skill_path.read_text(encoding="utf-8")
    section_match = re.search(
        r"## Required skills\s*\n(.*?)(?:\n## |\Z)", text, re.DOTALL
    )
    if not section_match:
        return set()

    skills = set()
    for line in section_match.group(1).splitlines():
        match = re.match(r"^\s*-\s*`([^`]+)`", line)
        if match:
            skills.add(match.group(1).strip())
    return skills


def parse_frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    data = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip().strip('"').strip("'")
    return data


def verify_manifest(repo_root: Path) -> list[str]:
    errors = []
    manifest_path = repo_root / "set-it-up" / "skills.json"
    vmode_path = repo_root / "vmode" / "SKILL.md"

    if not manifest_path.is_file():
        return [f"Missing manifest file: {manifest_path}"]

    try:
        with open(manifest_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        return [f"Malformed json in {manifest_path}: {exc}"]

    skills = data.get("skills", [])
    seen_names = set()
    manifest_required = set()

    for idx, entry in enumerate(skills):
        name = entry.get("name")
        if not name:
            errors.append(f"Entry index {idx} is missing 'name'")
            continue

        if name in seen_names:
            errors.append(f"Duplicate entry for '{name}' in manifest")
        seen_names.add(name)

        source = entry.get("source")
        if not source:
            errors.append(f"Skill '{name}' is missing 'source'")

        scope = entry.get("scope")
        if scope not in ("mine", "external"):
            errors.append(
                f"Skill '{name}' has invalid scope '{scope}' (must be 'mine' or 'external')"
            )

        if (
            scope == "mine"
            and source
            and not (source.startswith("vuon9/") or source == "local")
        ):
            errors.append(
                f"Skill '{name}' marked 'mine' must source from 'vuon9/*' or 'local', got '{source}'"
            )

        if entry.get("required"):
            manifest_required.add(name)

        if source == "vuon9/vstack":
            local_skill_dir = (
                repo_root / name
                if (repo_root / name).is_dir()
                else repo_root / "skills" / name
            )
            skill_md = local_skill_dir / "SKILL.md"
            readme_md = local_skill_dir / "README.md"

            if not skill_md.is_file():
                errors.append(f"Skill '{name}' is missing {skill_md}")
            else:
                meta = parse_frontmatter(skill_md)
                front_name = meta.get("name")
                if front_name and front_name != name:
                    errors.append(
                        f"Frontmatter name '{front_name}' in {skill_md} != manifest name '{name}'"
                    )
                desc = meta.get("description", "")
                if desc and not desc.startswith("Use when"):
                    errors.append(
                        f"Description for '{name}' in {skill_md} should start with 'Use when'"
                    )

            if not readme_md.is_file():
                errors.append(f"Skill '{name}' is missing {readme_md}")

    if vmode_path.is_file():
        vmode_required = parse_vmode_required(vmode_path)
        only_in_manifest = manifest_required - vmode_required
        only_in_vmode = vmode_required - manifest_required

        if only_in_manifest or only_in_vmode:
            errors.append(
                f"required skill mismatch between skills.json and vmode/SKILL.md: "
                f"manifest only={sorted(only_in_manifest)}, vmode only={sorted(only_in_vmode)}"
            )

    return errors


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    errors = verify_manifest(repo_root)
    if errors:
        print("Verification failed with errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
    print("Verification passed successfully.")


if __name__ == "__main__":
    main()
