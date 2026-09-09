import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "set-it-up" / "scripts"))

from verify import verify_manifest


class TestVerifyManifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "set-it-up").mkdir(parents=True)
        (self.root / "vmode").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_required_skill_reports_error(self):
        favorites = {
            "skills": [
                {
                    "name": "alpha",
                    "source": "vuon9/vstack",
                    "scope": "mine",
                    "required": True,
                }
            ]
        }
        with open(self.root / "set-it-up" / "skills.json", "w") as fh:
            json.dump(favorites, fh)

        vmode_content = "---\nname: vmode\n---\n## Required skills\n\n- `beta`\n"
        with open(self.root / "vmode" / "SKILL.md", "w") as fh:
            fh.write(vmode_content)

        errors = verify_manifest(self.root)
        self.assertTrue(any("required skill mismatch" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
