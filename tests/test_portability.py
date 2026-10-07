"""Checks that the skill runs on macOS, Windows, Linux, and WSL (issue #13).

Run: python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = [ROOT / "SKILL.md", ROOT / "README.md", *sorted((ROOT / "reference").glob("*.md"))]
TEMPLATE = ROOT / "reference" / "local-template.md"


def section(text, heading):
    m = re.search(rf"^##+ {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        raise AssertionError(f"missing section: {heading}")
    return m.group(1)


class NoHardcodedPython(unittest.TestCase):
    def test_script_calls_use_python_cmd(self):
        for doc in DOCS:
            with self.subTest(doc=doc.name):
                hits = re.findall(r"(?m)^.*\bpython3? scripts/\S+", doc.read_text(encoding="utf-8"))
                self.assertEqual(hits, [])


class NoWslDefault(unittest.TestCase):
    def test_no_mnt_c_in_scripts_or_docs(self):
        for f in [*sorted((ROOT / "scripts").glob("*.py")), *DOCS]:
            text = f.read_text(encoding="utf-8")
            if f == TEMPLATE:
                # One student's values, labelled as an example, not a default.
                text = text.replace(section(text, "Example (the author's values)"), "")
            with self.subTest(file=f.name):
                self.assertNotIn("/mnt/c", text)


class PythonCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TEMPLATE.read_text(encoding="utf-8")
        cls.body = section(cls.text, "Python check")

    def test_tries_the_three_commands_in_order(self):
        order = [self.body.find(c) for c in ("`python3`", "`python`", "`py -3`")]
        self.assertNotIn(-1, order, order)
        self.assertEqual(order, sorted(order))

    def test_requires_3_8(self):
        self.assertIn("3.8", self.body)

    def test_records_python_cmd_and_never_installs(self):
        self.assertIn("`python_cmd`", self.body)
        self.assertRegex(self.body, r"(?i)do not install")

    def test_checks_again_only_when_the_command_fails(self):
        self.assertRegex(self.body, r"(?i)fails")

    def test_runs_before_the_first_run_questions(self):
        self.assertLess(self.text.find("## Python check"), self.text.find("## First-run questions"))

    def test_skill_step_1_points_at_it(self):
        step1 = section((ROOT / "SKILL.md").read_text(encoding="utf-8"), "1. Load the personal settings")
        self.assertIn("Python check", step1)


class DownloadsDir(unittest.TestCase):
    def test_first_run_offers_the_detected_folder(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        questions = section(text, "First-run questions")
        self.assertIn("`downloads_dir`", questions)
        self.assertIn("scripts/downloads_dir.py", questions)

    def test_readme_names_the_python_requirement(self):
        self.assertIn("Python 3.8", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
