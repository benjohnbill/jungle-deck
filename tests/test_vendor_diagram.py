"""Contract checks for the vendored diagram-design copy.

The figure Verify step runs both vendored scripts, so they must run on every
Python that the README promises. CI runs this file on the whole matrix.

Run: python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "diagram-design"
SKILL = (VENDOR / "SKILL.md").read_text(encoding="utf-8")
EXAMPLES = sorted((VENDOR / "assets").glob("example-*-dark.html"))


class VerifyScriptsTest(unittest.TestCase):
    def check(self, script):
        self.assertTrue(EXAMPLES)
        for example in EXAMPLES:
            with self.subTest(example=example.name):
                result = subprocess.run(
                    [sys.executable, str(VENDOR / "scripts" / script), str(example)],
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0,
                                 result.stderr.decode("utf-8", "replace"))

    def test_self_check_runs_on_this_python(self):
        self.check("self_check.py")

    def test_verify_geometry_runs_on_this_python(self):
        self.check("verify-geometry.py")


class PythonCommandTest(unittest.TestCase):
    def test_skill_never_hardcodes_python(self):
        self.assertEqual(re.findall(r"\bpython3?\s\S*", SKILL), [])

    def test_verify_step_names_python_cmd(self):
        verify = next(line for line in SKILL.splitlines() if line.startswith("**Verify.**"))
        self.assertIn("<python_cmd> <this folder>/scripts/self_check.py", verify)
        self.assertIn("<python_cmd> <this folder>/scripts/verify-geometry.py", verify)
        self.assertIn("`python_cmd`", verify)


if __name__ == "__main__":
    unittest.main()
