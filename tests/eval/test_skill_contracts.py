"""Level 1: static skill and playbook contract checks (0% LLM, <100ms).

Runs against the repository itself (not ~/.agents) so CI works on a clean
checkout. Every check is deterministic and needs no network or API keys.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VSTACK_DIR = REPO_ROOT / "vmode"
SETUP_DIR = REPO_ROOT / "set-it-up"
SKILLS_DIR = REPO_ROOT / "skills"

REQUIRED_SKILLS = {
    "brainstorming",
    "wayfinder",
    "test-driven-development",
    "unslop",
    "hunk-review",
    "requesting-code-review",
    "receiving-code-review",
}

EM_DASH = "\u2014"


def _frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, ""
    data = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip('"').strip("'")
    return data, parts[2]


class TestSkillFrontmatter(unittest.TestCase):
    """Every local skill folder has valid frontmatter with name + description."""

    def _local_skill_dirs(self):
        dirs = [VSTACK_DIR, SETUP_DIR]
        if SKILLS_DIR.is_dir():
            dirs += [
                d for d in sorted(SKILLS_DIR.iterdir()) if (d / "SKILL.md").is_file()
            ]
        return [d for d in dirs if (d / "SKILL.md").is_file()]

    def test_all_local_skills_have_valid_frontmatter(self):
        for skill_dir in self._local_skill_dirs():
            skill_md = skill_dir / "SKILL.md"
            meta, _ = _frontmatter(skill_md)
            with self.subTest(skill=skill_dir.name):
                self.assertTrue(meta.get("name"), f"{skill_md} missing name")
                self.assertRegex(meta["name"], r"^[a-z0-9-]+$")
                desc = meta.get("description", "")
                self.assertTrue(desc, f"{skill_md} missing description")
                self.assertTrue(
                    desc.startswith("Use when"),
                    f"{skill_md} description must start with 'Use when'",
                )
                self.assertEqual(
                    meta["name"], skill_dir.name, "frontmatter name != folder"
                )

    def test_every_local_skill_has_readme(self):
        for skill_dir in self._local_skill_dirs():
            with self.subTest(skill=skill_dir.name):
                self.assertTrue(
                    (skill_dir / "README.md").is_file(),
                    f"{skill_dir.name} missing README.md",
                )


class TestRequiredSkillDependencies(unittest.TestCase):
    """Skills listed in vmode's Required skills section are tracked and installed.

    Required skills are a mix of repo-vendored skills and external favorites
    (obra/superpowers, modem-dev/hunk). Existence means: present in the repo
    folder when vendored, or present as a skills.json entry when external.
    """

    def setUp(self):
        self.manifest = json.loads(
            (SETUP_DIR / "skills.json").read_text(encoding="utf-8")
        )["skills"]

    def _manifest_source(self, name):
        for entry in self.manifest:
            if entry.get("name") == name:
                return entry.get("source") or ""
        return ""

    def test_required_skills_exist_on_disk(self):
        text = (VSTACK_DIR / "SKILL.md").read_text(encoding="utf-8")
        section = re.search(
            r"## Required skills\s*\n(.*?)(?:\n## |\Z)", text, re.DOTALL
        )
        assert section is not None, "vmode SKILL.md has no Required skills section"
        listed = set(re.findall(r"-\s*`([a-z0-9-]+)`", section.group(1)))
        self.assertEqual(
            listed, REQUIRED_SKILLS, "required list drifted from canonical set"
        )
        for skill in sorted(listed):
            vendored = (SKILLS_DIR / skill).is_dir() or (REPO_ROOT / skill).is_dir()
            tracked = skill in [e.get("name") for e in self.manifest]
            self.assertTrue(
                vendored or tracked,
                f"required skill '{skill}' neither vendored nor in skills.json",
            )

    def test_required_skills_marked_required_in_manifest(self):
        listed_names = [e.get("name") for e in self.manifest if e.get("required")]
        missing = REQUIRED_SKILLS - set(listed_names)
        self.assertEqual(
            missing,
            set(),
            f"required skills missing required:true in skills.json: {missing}",
        )


class TestRuleCompliance(unittest.TestCase):
    """Playbooks and skill docs comply with vmode's writing rules."""

    def _markdown_files(self):
        files = []
        for base in (VSTACK_DIR, SETUP_DIR):
            for path in sorted(base.rglob("*.md")):
                files.append(path)
        if SKILLS_DIR.is_dir():
            for path in sorted(SKILLS_DIR.rglob("*.md")):
                files.append(path)
        return files

    def test_no_em_dashes_in_vmode_playbooks(self):
        targets = list((VSTACK_DIR / "playbooks").glob("*.md"))
        targets.append(VSTACK_DIR / "SKILL.md")
        for path in targets:
            with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(EM_DASH, path.read_text(encoding="utf-8"))

    def test_no_narrative_comment_placeholders_in_repo(self):
        # Banned narrating-comment patterns. vmode docs cite them as the
        # counterexample to avoid, so skip the rule-definition text itself and
        # only scan code-fenced blocks in templates.
        pattern = re.compile(r"//\s*(Phase \d+|Step \d+)")
        for path in self._markdown_files():
            text = path.read_text(encoding="utf-8")
            for block in re.findall(r"```[^`]*```", text, re.DOTALL):
                with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                    self.assertIsNone(
                        pattern.search(block),
                        f"narrating comment pattern in code block of {path.relative_to(REPO_ROOT)}",
                    )


class TestRoleBriefTemplates(unittest.TestCase):
    """roles.md brief templates contain the evidence-return clauses (W6/W1 fixes)."""

    def setUp(self):
        self.roles = (VSTACK_DIR / "references" / "roles.md").read_text(
            encoding="utf-8"
        )

    def test_general_brief_requires_raw_evidence(self):
        self.assertIn("git diff --stat", self.roles)
        self.assertIn("Return", self.roles)
        self.assertRegex(
            self.roles, r"raw execution evidence|raw .*evidence|unsubstantiated claims"
        )

    def test_research_brief_requires_grep_anchored_citations(self):
        self.assertIn("grep -n", self.roles)
        self.assertIn("citations", self.roles)

    def test_watchdog_brief_uses_gh_pr_checks(self):
        self.assertIn("gh pr checks", self.roles)


if __name__ == "__main__":
    unittest.main()
