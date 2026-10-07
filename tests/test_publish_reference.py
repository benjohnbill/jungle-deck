"""Contract checks for reference/publish.md (SPEC D12, D13, D14, D17; issue #9).

Run: python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLISH = ROOT / "reference" / "publish.md"
SCRIPT = ROOT / "scripts" / "publish.py"

# The publish steps, as `### N. <title>` headings, in D12 order.
STEPS = [
    "Commit in the week repo",
    "Copy the deck",
    "Draft the index card",
    "Commit in the Pages repo",
    "Ask once",
    "Push both repos",
    "Verify the live deck",
    "DESIGN.md",
    "Close the BRIEF",
]


def step(text, title):
    """Return the body of the `### N. title` step, up to the next heading."""
    m = re.search(rf"^### \d+\. {re.escape(title)}[^\n]*\n(.*?)(?=^##|\Z)",
                  text, re.S | re.M)
    if not m:
        raise AssertionError(f"no '### N. {title}' step")
    return m.group(1)


def flat(text):
    """Collapse line wraps so a phrase can span two lines."""
    return re.sub(r"\s+", " ", text)


class PublishReferenceTest(unittest.TestCase):
    def setUp(self):
        self.text = PUBLISH.read_text(encoding="utf-8")

    def test_steps_in_d12_order(self):
        found = re.findall(r"^### (\d+)\. (.+)$", self.text, re.M)
        titles = [t for _, t in found]
        positions = []
        for title in STEPS:
            hits = [i for i, t in enumerate(titles) if t.startswith(title)]
            self.assertTrue(hits, f"step '{title}' missing")
            positions.append(hits[0])
        self.assertEqual(positions, sorted(positions), "steps out of order")
        numbers = [int(n) for n, _ in found]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)), "step numbers")

    def test_week_repo_commit_set_and_gitignore(self):
        body = step(self.text, "Commit in the week repo")
        # The lines are added at build time (reference/build.md); here only checked.
        self.assertRegex(flat(body), r"(?i)(check|verify) that `\.gitignore`")
        self.assertNotRegex(flat(body), r"(?i)add each of these lines")
        for line in ["_backup/", "previews/", ".impeccable/"]:
            self.assertIn(f"`{line}`", body, f"gitignore '{line}'")
        for item in ["BRIEF.md", "evidence/", ".html"]:
            self.assertIn(item, body, f"commit set lacks '{item}'")

    def test_stage_named_files_never_add_all(self):
        self.assertRegex(self.text, r"(?i)stage named files only")
        self.assertRegex(self.text, r"Never use `git add -A`")
        for cmd in re.findall(r"(?m)^\s*(git (?:-C \S+ )?add .*)$", self.text):
            self.assertNotRegex(cmd, r"\s(-A|\.|--all)(\s|$)", f"bulk add: {cmd}")

    def test_card_uses_absolute_url_from_brief(self):
        body = step(self.text, "Draft the index card")
        self.assertIn("<pages_url_base>study/weekNN/<deck-slug>.html", body)
        self.assertRegex(body, r"(?i)full absolute URL as the `href`")
        self.assertRegex(body, r"(?i)do not use a relative href")
        self.assertIn("BRIEF.md", body)

    def test_never_edit_the_pages_copy(self):
        self.assertRegex(self.text, r"(?i)never edit the pages copy")
        verify = flat(step(self.text, "Verify the live deck"))
        self.assertRegex(verify, r"(?i)fix the source deck")
        self.assertRegex(verify, r"(?i)do not edit the pages copy")

    def test_push_only_after_explicit_yes_asked_once(self):
        ask = step(self.text, "Ask once")
        self.assertRegex(ask, r"(?i)push only after an explicit yes")
        self.assertRegex(ask, r"(?i)if the answer is not a yes, stop")
        rules = re.search(r"^## Rules\n(.*?)(?=^## )", self.text, re.S | re.M)
        self.assertTrue(rules, "no '## Rules' section")
        self.assertRegex(flat(rules.group(1)), r"(?i)push only after an explicit yes")
        self.assertRegex(self.text, r"(?i)ask for the push once")
        self.assertRegex(step(self.text, "Push both repos"), r"(?i)week repo.*pages repo")

    def test_design_md_items_applied_only_when_picked(self):
        body = step(self.text, "DESIGN.md")
        self.assertRegex(body, r"(?i)\bdiff\b")
        self.assertRegex(body, r"(?i)apply only the items the student picks")
        self.assertRegex(body, r"(?i)picks none, do not change DESIGN\.md")

    def test_extraction_offered_when_design_md_empty(self):
        body = flat(step(self.text, "DESIGN.md"))
        empty = body[body.index("If `design_md` is empty"):]
        self.assertRegex(empty, r"(?i)offer to extract a DESIGN\.md")
        self.assertIn("Google Labs DESIGN.md format", empty)
        self.assertRegex(empty, r"`design_md` in `jungle-deck\.local\.md`")

    def test_empty_pages_repo_stops_after_week_repo_commit(self):
        body = step(self.text, "Commit in the week repo")
        m = re.search(r"If `pages_repo` is empty, stop[^.]*", body)
        self.assertTrue(m, "no stop rule for empty pages_repo in step 1")
        tail = body[m.start():]
        for skipped in ["do not copy", "do not push", "card"]:
            self.assertIn(skipped, tail.lower())

    def rules(self):
        m = re.search(r"^## Rules\n(.*?)(?=^## )", self.text, re.S | re.M)
        self.assertTrue(m, "no '## Rules' section")
        return flat(m.group(1))

    def test_card_rule_has_one_exception_relative_href_to_absolute(self):
        rules = self.rules()
        self.assertRegex(rules, r"(?i)do not remove or rewrite an existing card")
        self.assertRegex(rules, r"(?i)exactly one exception")
        self.assertRegex(rules, r"(?i)same deck URL[^.]*href[^.]*from relative to absolute")
        self.assertRegex(rules, r"(?i)nothing else of an existing card changes")
        card = flat(step(self.text, "Draft the index card"))
        self.assertRegex(card, r"(?i)change only that href to the absolute URL")

    def test_final_brief_commit_stays_local_and_student_is_told(self):
        body = flat(step(self.text, "Close the BRIEF"))
        self.assertRegex(body, r"(?i)commit stays local")
        self.assertRegex(body, r"(?i)tell the student")
        self.assertRegex(body, r"(?i)next push of the week repo")
        self.assertRegex(body, r"(?i)no second (push )?confirmation")

    def test_done_is_last(self):
        body = step(self.text, "Close the BRIEF")
        self.assertIn("phase: done", body)
        self.assertRegex(body, r"(?i)only when the student confirms")

    def test_cli_lines_match_publish_py_help(self):
        lines = re.findall(r"(?m)^\s*python3 scripts/publish\.py (\w+)(.*)$", self.text)
        self.assertEqual({c for c, _ in lines}, {"copy", "verify"}, "copy and verify lines")
        for command, rest in lines:
            help_text = subprocess.run(
                [sys.executable, str(SCRIPT), command, "--help"],
                capture_output=True, text=True, check=True).stdout
            usage = help_text.split("\n\n")[0]
            flags = re.findall(r"--[\w-]+", rest)
            self.assertIn("--deck", flags)
            self.assertIn("--week", flags)
            for flag in flags:
                self.assertIn(flag, help_text, f"{command}: unknown flag {flag}")
            # Every flag that the script requires appears in the quoted line.
            required = re.findall(r"(?<!\[)(--[\w-]+) [A-Z]+", usage)
            for flag in required:
                self.assertIn(flag, flags, f"{command}: required {flag} not quoted")
        for flag in re.findall(r"`(--[\w-]+)`", self.text):
            help_all = "".join(subprocess.run(
                [sys.executable, str(SCRIPT), c, "--help"],
                capture_output=True, text=True, check=True).stdout
                for c in ("copy", "verify"))
            self.assertIn(flag, help_all, f"prose names unknown flag {flag}")


if __name__ == "__main__":
    unittest.main()
