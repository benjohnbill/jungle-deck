"""SPEC D24: no author-specific values ship.

Every file in `git ls-files` is checked, except SPEC.md, LICENSE, and the
README clone-URL lines. The banned strings are split in this file, so the
check passes on its own source.

Run: python3 -m unittest discover -s tests
"""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BANNED = ["benjohn" "bill", "/mnt/c/" "Users/", "krafton-" "jungle/", "week_repo" "_root"]
EXCLUDED_FILES = {"SPEC.md", "LICENSE"}
CLONE_LINE = re.compile(r"^\s*git clone https://github\.com/[\w.-]+/jungle-deck\b")


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True,
                         capture_output=True).stdout.decode()
    return [f for f in out.split("\0") if f and f not in EXCLUDED_FILES]


class NoAuthorValuesTest(unittest.TestCase):
    def test_tracked_files_hold_no_author_values(self):
        files = tracked_files()
        self.assertIn("SKILL.md", files)
        hits = []
        for f in files:
            try:
                text = (ROOT / f).read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for n, line in enumerate(text.splitlines(), 1):
                if f == "README.md" and CLONE_LINE.match(line):
                    continue
                hits += [f"{f}:{n}: {b}" for b in BANNED if b in line]
        self.assertEqual(hits, [])

    def test_untracked_files_are_not_checked(self):
        self.assertNotIn("jungle-deck.local.md", tracked_files())


if __name__ == "__main__":
    unittest.main()
