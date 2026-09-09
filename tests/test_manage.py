import subprocess
import sys
import unittest


class TestManageCLI(unittest.TestCase):
    def test_manage_verify_command_runs(self):
        res = subprocess.run(
            [sys.executable, "set-it-up/scripts/manage.py", "verify"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=f"manage verify failed: {res.stderr}")
        self.assertIn("Verification passed", res.stdout)


if __name__ == "__main__":
    unittest.main()
