import subprocess
import sys
import unittest


class TestInstallDryRun(unittest.TestCase):
    def test_install_dry_run_flag(self):
        res = subprocess.run(
            [sys.executable, "set-it-up/scripts/install.py", "--required", "--dry-run"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("[dry-run]", res.stdout)


if __name__ == "__main__":
    unittest.main()
