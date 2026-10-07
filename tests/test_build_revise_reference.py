"""Contract checks for reference/build.md and reference/revise.md
(SPEC D9, D10, D11, D17; issue #8).

Run: python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "reference" / "build.md"
REVISE = ROOT / "reference" / "revise.md"
PULL = ROOT / "scripts" / "pull_edits.py"

# Repo paths a reader of these docs is sent to. Placeholders such as
# <week repo>/study/<slug>/ are not repo paths and are not matched.
REPO_PATH = re.compile(
    r"`((?:reference|templates|scripts|vendor|tests)/[\w./-]+)`")


def section(text, heading):
    """Return the body of the `## heading` section, up to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)",
                  text, re.S | re.M)
    if not m:
        raise AssertionError(f"no '## {heading}' section")
    return m.group(1)


def flat(text):
    """Collapse line wraps so a phrase can span two lines."""
    return re.sub(r"\s+", " ", text)


class PathsExist:
    """Mixin: every repo path a doc names exists."""

    def test_named_paths_exist(self):
        paths = REPO_PATH.findall(self.text)
        self.assertTrue(paths, "doc names no repo path")
        for p in paths:
            self.assertTrue((ROOT / p).exists(), f"named path missing: {p}")


class BuildReferenceTest(PathsExist, unittest.TestCase):
    def setUp(self):
        self.text = BUILD.read_text(encoding="utf-8")

    def test_style_source_order(self):
        body = flat(section(self.text, "Style source"))
        sources = ["`design_md`", "frontend-slides", "Phase 2",
                   "vendor/frontend-slides/STYLE_PRESETS.md"]
        positions = [body.find(s) for s in sources]
        self.assertNotIn(-1, positions, f"missing a source of {sources}")
        self.assertEqual(positions, sorted(positions), "style sources out of order")
        self.assertIn(":root", body)
        self.assertRegex(body, r"Do's and Don'ts")
        self.assertRegex(body, r"(?i)only (if|when) .*installed")

    def test_starts_from_stage_template_at_deck_path(self):
        body = flat(section(self.text, "Start from the stage template"))
        self.assertIn("templates/stage.html", body)
        self.assertIn("<week repo>/study/<slug>/<slug>.html", body)
        self.assertRegex(body, r"(?i)keep .*section id")

    def test_theses_verbatim(self):
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)verbatim")
        self.assertRegex(body, r"(?i)do not (rephrase|reword)")

    def test_evidence_only_from_real_runs(self):
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)only from real runs")
        self.assertIn("evidence/", body)
        self.assertRegex(body, r"(?i)if the (log|file) is missing, (re-?run|run) the command")
        self.assertRegex(body, r"(?i)never (invent|write|type) output")

    def test_terms_and_light_notes(self):
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)define .*on (the )?screen|on-screen definition")
        self.assertRegex(body, r"(?i)light suggested script")

    def test_no_timer_gate(self):
        text = flat(self.text)
        self.assertRegex(text, r"(?i)background, not a gate")
        self.assertRegex(text, r"(?i)no timer check")
        self.assertRegex(text, r"(?i)do not cut content only to fit")
        # No seconds budget stated as a rule.
        self.assertNotRegex(text, r"\b120\b")
        self.assertNotRegex(text, r"(?i)(must|should) (fit|stay) (in|within|under) (2|two) min")

    def test_viewport_and_density(self):
        text = flat(self.text)
        self.assertIn("vendor/frontend-slides/viewport-base.css", text)
        self.assertIn("1280×720", text)
        self.assertIn("1920×1080", text)
        self.assertRegex(text, r"(?i)density")
        self.assertRegex(text, r"(?i)never scroll")

    def test_phase_moves_to_revise_only_on_confirmation(self):
        body = flat(section(self.text, "Finish"))
        self.assertRegex(body, r"`phase` to `revise`")
        self.assertRegex(body, r"(?i)only when the student confirms")


class ReviseReferenceTest(PathsExist, unittest.TestCase):
    def setUp(self):
        self.text = REVISE.read_text(encoding="utf-8")

    def loop(self):
        return flat(section(self.text, "The loop"))

    def test_loop_steps_in_order(self):
        body = self.loop()
        marks = ["`E`", "Ctrl+S", "pull_edits.py", "--write", "layout"]
        positions = [body.find(m) for m in marks]
        self.assertNotIn(-1, positions, f"missing a step of {marks}")
        self.assertEqual(positions, sorted(positions), "loop steps out of order")

    def test_dry_run_before_write_after_agreement(self):
        body = self.loop()
        self.assertRegex(body, r"(?i)dry-run first")
        self.assertRegex(body, r"(?i)show the student the summary")
        self.assertRegex(body, r"(?i)only after the student agrees")

    def test_backup_or_commit_before_write(self):
        body = self.loop()
        backup = re.search(r"(?i)commit .*or copy .*deck", body)
        self.assertTrue(backup, "no commit-or-copy step")
        self.assertLess(backup.start(), body.find("--write"),
                        "backup step must come before --write")
        self.assertRegex(flat(self.text), r"(?i)no backup")

    def test_keeps_student_wording(self):
        self.assertRegex(flat(self.text), r"(?i)do not (overwrite|change|rephrase) the student's wording")

    def test_records_changes_in_brief(self):
        self.assertRegex(flat(self.text), r"(?i)`Revise` (section|table) of `BRIEF\.md`")

    def test_leaves_only_when_student_says_publish(self):
        body = flat(section(self.text, "Leaving revise"))
        self.assertRegex(body, r"`phase` to `publish`")
        self.assertRegex(body, r"(?i)only when the student says to publish")
        self.assertRegex(body, r"(?i)do not (propose|suggest|ask) .*publish")

    def test_cli_lines_match_pull_edits_help(self):
        help_text = subprocess.run(
            [sys.executable, str(PULL), "--help"],
            capture_output=True, text=True, check=True).stdout
        usage = help_text.split("\n\n")[0]
        # Optional groups may wrap across lines; drop them, keep the rest.
        required = re.findall(r"--[\w-]+", re.sub(r"\[[^\]]*\]", "", usage, flags=re.S))
        lines = re.findall(r"(?m)^\s*python3 \S*scripts/pull_edits\.py(.*)$", self.text)
        self.assertGreaterEqual(len(lines), 2, "need a dry-run line and a --write line")
        self.assertTrue(any("--write" not in l for l in lines), "no dry-run line")
        self.assertTrue(any("--write" in l for l in lines), "no --write line")
        for rest in lines:
            flags = re.findall(r"--[\w-]+", rest)
            for flag in flags:
                self.assertIn(flag, help_text, f"unknown flag {flag}")
            for flag in required:
                self.assertIn(flag, flags, f"required {flag} not quoted")
        for span in re.findall(r"`([^`\n]+)`", self.text):
            for flag in re.findall(r"(?<![\w-])--[\w-]+", span):
                self.assertIn(flag, help_text, f"prose names unknown flag {flag}")


if __name__ == "__main__":
    unittest.main()
