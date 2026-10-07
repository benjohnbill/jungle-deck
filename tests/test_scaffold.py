"""Acceptance checks for T1 (scaffold): README, vendored frontend-slides, MIT LICENSE.

Run: python3 -m unittest discover -s tests

The byte-identity check reads the upstream files at the commit recorded in
vendor/frontend-slides/SOURCE.md, from a local frontend-slides git checkout
(FRONTEND_SLIDES_DIR, default: the Claude Code marketplace copy). It is skipped
when no checkout is present.
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "frontend-slides"
VENDORED = ["LICENSE", "viewport-base.css", "STYLE_PRESETS.md",
            "html-template.md", "animation-patterns.md"]
UPSTREAM_URL = "https://github.com/zarazhangrui/frontend-slides"
UPSTREAM_DIR = Path(os.environ.get(
    "FRONTEND_SLIDES_DIR",
    Path.home() / ".claude/plugins/marketplaces/frontend-slides"))


def recorded_commit():
    text = (VENDOR / "SOURCE.md").read_text()
    m = re.search(r"\b([0-9a-f]{40})\b", text)
    if not m:
        raise AssertionError("SOURCE.md records no 40-hex upstream commit")
    return m.group(1)


class ReadmeTest(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "README.md").read_text()

    def test_states_install_by_clone(self):
        self.assertIn("git clone https://github.com/benjohnbill/jungle-deck "
                      "~/.claude/skills/jungle-deck", self.text)

    def test_states_first_run(self):
        self.assertRegex(self.text, r"(?im)^#+\s*first run")

    def test_credits_frontend_slides_with_link(self):
        self.assertRegex(self.text, r"(?im)^#+\s*credits")
        self.assertIn(UPSTREAM_URL, self.text)


class VendorTest(unittest.TestCase):
    def test_all_files_present(self):
        for name in VENDORED + ["SOURCE.md"]:
            self.assertTrue((VENDOR / name).is_file(), name)

    def test_license_is_mit(self):
        text = (VENDOR / "LICENSE").read_text()
        self.assertTrue(text.startswith("MIT License"))
        self.assertIn("Zara Zhang", text)

    def test_source_note_names_upstream_and_commit(self):
        self.assertIn(UPSTREAM_URL, (VENDOR / "SOURCE.md").read_text())
        recorded_commit()

    @unittest.skipUnless((UPSTREAM_DIR / ".git").exists(),
                         "no local frontend-slides checkout")
    def test_byte_identical_to_upstream_commit(self):
        commit = recorded_commit()
        for name in VENDORED:
            upstream = subprocess.run(
                ["git", "-C", str(UPSTREAM_DIR), "show", f"{commit}:{name}"],
                check=True, capture_output=True).stdout
            self.assertEqual((VENDOR / name).read_bytes(), upstream, name)


if __name__ == "__main__":
    unittest.main()
