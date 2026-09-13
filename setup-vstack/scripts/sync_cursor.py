#!/usr/bin/env python3
"""Refresh vendored cursor/plugins skills that are unmodified from upstream.

`code-teach`, `bro`, and `unslop` are copies of cursor/plugins skills kept
under the same or a new name (only `code-teach` is renamed). They are
unmodified, so this can overwrite them from upstream. `how` and `why` are NOT
included because they are edited and must be refreshed manually.
"""

import os
import re
import subprocess
import sys

# id = cursor/plugins pstack/skills/<id>/SKILL.md; dest = path in the collection;
# rename = (upstream frontmatter name, collection name) for renamed skills.
VENDORED = [
    {
        "id": "teach",
        "dest": "skills/code-teach/SKILL.md",
        "rename": ("teach", "code-teach"),
    },
    {"id": "bro", "dest": "skills/bro/SKILL.md"},
    {"id": "unslop", "dest": "skills/unslop/SKILL.md"},
]

BASE = (
    "https://raw.githubusercontent.com/cursor/plugins/main/pstack/skills/{id}/SKILL.md"
)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")


def main():
    errors = []
    for entry in VENDORED:
        url = BASE.format(id=entry["id"])
        dest = os.path.join(REPO, entry["dest"])

        res = subprocess.run(["curl", "-fsSL", url], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"fetch failed: {entry['id']}: {res.stderr}", file=sys.stderr)
            errors.append(entry["id"])
            continue

        content = res.stdout
        if entry.get("rename"):
            old, new = entry["rename"]
            pattern = rf"(?m)^name:\s*{re.escape(old)}\s*$"
            content, n = re.subn(pattern, f"name: {new}", content, count=1)
            if n != 1:
                print(
                    f"warning: {entry['id']} frontmatter changed; name not rewritten.",
                    file=sys.stderr,
                )

        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w") as fh:
                fh.write(content)
        except OSError as exc:
            raise RuntimeError(f"could not write {dest}: {exc}") from exc
        print(f"synced {entry['id']} -> {os.path.relpath(dest)}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
