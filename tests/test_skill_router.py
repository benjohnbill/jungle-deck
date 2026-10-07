"""Contract checks for SKILL.md, the router (SPEC D2, D4, D6, D15, D16, D19;
issue #10).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"

# D2, verbatim.
TRIGGERS = ["발표 덱", "발표 준비", "슬라이드 만들자", "jungle-deck 이어서", "덱 게시"]


def split_front_matter(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise AssertionError("SKILL.md has no YAML front matter")
    return m.group(1), m.group(2)


def front_matter_field(front, key):
    m = re.search(rf"(?m)^{key}:\s*(.+)$", front)
    return m.group(1).strip() if m else None


class FrontMatterTest(unittest.TestCase):
    def setUp(self):
        self.front, _ = split_front_matter(SKILL.read_text())

    def test_name_is_jungle_deck(self):
        self.assertEqual(front_matter_field(self.front, "name"), "jungle-deck")

    def test_description_names_every_d2_trigger(self):
        desc = front_matter_field(self.front, "description")
        self.assertIsNotNone(desc, "front matter has no description")
        for trigger in TRIGGERS:
            self.assertIn(trigger, desc)

    def test_description_says_when_to_use(self):
        desc = front_matter_field(self.front, "description")
        self.assertRegex(desc, r"\bUse when\b")


# Phase -> the reference file that runs it. `done` has no phase file; it
# routes to the BRIEF template, because the next step is a new deck.
PHASE_FILES = {
    "grill": "reference/grill.md",
    "build": "reference/build.md",
    "revise": "reference/revise.md",
    "publish": "reference/publish.md",
    "done": "reference/brief-template.md",
}


class RoutingTest(unittest.TestCase):
    def setUp(self):
        _, self.body = split_front_matter(SKILL.read_text())

    def test_each_phase_routes_to_its_reference_file(self):
        for phase, path in PHASE_FILES.items():
            with self.subTest(phase=phase):
                self.assertTrue((ROOT / path).exists(), path)
                rows = [line for line in self.body.splitlines()
                        if f"`{phase}`" in line and path in line]
                self.assertTrue(rows, f"no line routes `{phase}` to {path}")

    def test_reads_brief_before_dispatch(self):
        read = re.search(r"Read[^\n]*`?BRIEF\.md`?", self.body)
        self.assertIsNotNone(read, "no step says to read BRIEF.md")
        first_route = self.body.find(PHASE_FILES["build"])
        self.assertLess(read.start(), first_route)

    def test_no_brief_starts_at_grill(self):
        self.assertRegex(
            self.body,
            r"(?i)(no|missing)[^.]*BRIEF\.md[^.]*start[^.]*`grill`")


class FirstRunTest(unittest.TestCase):
    def setUp(self):
        _, self.body = split_front_matter(SKILL.read_text())

    def test_missing_local_md_is_created_from_template(self):
        self.assertRegex(
            self.body,
            r"(?i)jungle-deck\.local\.md`?[^.]*(missing|does not exist)"
            r"[^.]*reference/local-template\.md")

    def test_settings_come_before_the_deck(self):
        local = self.body.find("jungle-deck.local.md")
        self.assertNotEqual(local, -1)
        self.assertLess(local, self.body.find("Read `BRIEF.md`"))

    def test_local_md_is_gitignored(self):
        self.assertIn("jungle-deck.local.md",
                      (ROOT / ".gitignore").read_text().splitlines())


# D15: dependency -> a word its fallback cell must name.
FALLBACKS = {
    "grilling": "reference/grill.md",
    "frontend-slides": "vendor/frontend-slides/",
    "claude-mem": "skip",
    "Pages": "local HTML",
}


def section(body, heading):
    m = re.search(rf"(?ms)^## {heading}\n(.*?)(?=^## |\Z)", body)
    if not m:
        raise AssertionError(f"SKILL.md has no '## {heading}' section")
    return m.group(1)


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("|") and not re.match(r"^\|[-| ]+\|$", line):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:]  # drop the header row


class DependencyTest(unittest.TestCase):
    def setUp(self):
        _, body = split_front_matter(SKILL.read_text())
        self.rows = table_rows(section(body, "Dependencies"))

    def test_each_dependency_has_detection_and_named_fallback(self):
        for dep, fallback in FALLBACKS.items():
            with self.subTest(dep=dep):
                row = next((r for r in self.rows if dep in r[0]), None)
                self.assertIsNotNone(row, f"no row for {dep}")
                self.assertEqual(len(row), 3, row)
                _, detect, fall = row
                self.assertTrue(detect and detect != "—", f"{dep}: no detection")
                self.assertIn(fallback, fall)

    def test_pages_repo_without_git_is_an_error_not_the_fallback(self):
        # publish.py copy fails on a pages_repo with no .git (a typo).
        row = " ".join(next(r for r in self.rows if "Pages" in r[0]))
        self.assertRegex(row, r"(?i)`pages_repo` in local\.md is (empty|not empty)")
        self.assertRegex(row, r"(?i)no `\.git`[^|]*error")
        self.assertRegex(row, r"(?i)not the fallback")


class VerificationStateTest(unittest.TestCase):
    """D19: the skill states which phases a real deck has verified."""

    def setUp(self):
        _, body = split_front_matter(SKILL.read_text())
        self.text = section(body, "Verification state")
        self.flat = " ".join(self.text.split())

    def test_revise_and_publish_first_on_a_nearly_finished_deck(self):
        self.assertRegex(
            self.flat,
            r"`revise` and `publish`[^.]*first verified on a nearly finished deck")

    def test_grill_and_build_first_on_the_next_new_deck(self):
        self.assertRegex(
            self.flat, r"`grill` and `build`[^.]*first verified on the next new deck")

    def test_no_phase_verified_yet(self):
        self.assertRegex(self.flat, r"No phase has been verified on a real deck yet")


REPO_DIRS = ("reference/", "templates/", "scripts/", "vendor/", "tests/")
MAX_LINES = 120
SHINGLE = 10  # words; a shared run this long is a restated sentence


def words(text):
    return re.findall(r"[\w`'./-]+", text.lower())


def shingles(text, n=SHINGLE):
    w = words(text)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


class RouterOnlyTest(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text()

    def test_every_named_repo_path_exists(self):
        paths = [p for p in re.findall(r"`([^`\s]+)`", self.text)
                 if p.startswith(REPO_DIRS)]
        self.assertTrue(paths, "SKILL.md names no repo path")
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists(), path)

    def test_stays_short(self):
        self.assertLess(len(self.text.splitlines()), MAX_LINES)

    def test_does_not_restate_reference_files(self):
        mine = shingles(split_front_matter(self.text)[1])
        for ref in sorted((ROOT / "reference").glob("*.md")):
            with self.subTest(ref=ref.name):
                shared = mine & shingles(ref.read_text())
                self.assertFalse(shared, sorted(shared)[:3])


if __name__ == "__main__":
    unittest.main()
