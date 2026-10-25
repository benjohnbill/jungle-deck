"""Contract checks for SKILL.md, the router (SPEC D2, D3, D4, D5, D6, D15,
D16, D19, D23; issues #10, #23).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"

# D2, verbatim: the new phrases and the old ones that still trigger.
TRIGGERS = ["발표 자료 만들자", "발표 준비", "슬라이드 만들자", "jungle-deck 이어서",
            "발표 자료 게시", "발표 덱", "덱 게시"]


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
        self.front, _ = split_front_matter(SKILL.read_text(encoding="utf-8"))

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
    "design": "reference/design.md",
    "build": "reference/build.md",
    "revise": "reference/revise.md",
    "publish": "reference/publish.md",
    "done": "reference/brief-template.md",
}


class RoutingTest(unittest.TestCase):
    def setUp(self):
        _, self.body = split_front_matter(SKILL.read_text(encoding="utf-8"))

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

    def test_phase_rows_follow_the_d3_order(self):
        order = [self.body.find(f"| `{p}` |") for p in
                 ("grill", "design", "build", "revise", "publish", "done")]
        self.assertNotIn(-1, order, order)
        self.assertEqual(order, sorted(order))

    def test_resume_points_to_brief_template_hooks(self):
        find_brief = re.search(r"(?ms)^### 2\. Find the BRIEF\n(.*?)(?=^### )",
                               self.body).group(1)
        for hook in ("How to resume", "kind: jungle-deck", "current_brief",
                     "prev_brief", "Migration from the old format"):
            with self.subTest(hook=hook):
                self.assertIn(hook, find_brief)

    def test_no_brief_starts_at_grill(self):
        self.assertRegex(
            self.body,
            r"(?i)(no|missing)[^.]*BRIEF\.md[^.]*start[^.]*`grill`")


class FirstRunTest(unittest.TestCase):
    def setUp(self):
        _, self.body = split_front_matter(SKILL.read_text(encoding="utf-8"))

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
                      (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())


# D15: dependency -> a word its fallback cell must name.
FALLBACKS = {
    "grilling": "reference/grill.md",
    "frontend-slides": "vendor/frontend-slides/",
    "claude-mem": "skip",
    "gh": "REST API",
    "Revise server": "scripts/pull_edits.py",
    "Monitor": "tells you after each save",
    "Pages": "local HTML",
    "Headless browser": "student preview",
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


class NoReadBeforeOpeningTest(unittest.TestCase):
    """D8: a verify run caught `git log` in the BRIEF search, before the opening answer."""

    def test_find_step_reads_no_repo_history(self):
        _, body = split_front_matter(SKILL.read_text(encoding="utf-8"))
        text = " ".join(section(body, "Steps").split())
        self.assertIn("git rev-parse --show-toplevel", text)
        self.assertRegex(text, r"(?i)no `git log`")
        self.assertRegex(text, r"(?i)before the student answers the opening question")


class SessionBreakTest(unittest.TestCase):
    """D27: one suggested new session, at design -> build."""

    def test_one_suggestion_at_design_to_build(self):
        _, body = split_front_matter(SKILL.read_text(encoding="utf-8"))
        text = section(body, "Steps")
        self.assertIn("새 세션에서 'jungle-deck 이어서'라고 하면 가볍게 이어져요", text)
        self.assertRegex(text, r"`design` to `build`")
        self.assertRegex(text, r"(?i)once")
        self.assertEqual(text.count("새 세션에서"), 1)
        # Run A (2026-10-26): the line came, then build started in the same turn.
        self.assertRegex(" ".join(text.split()), r"(?i)end your turn")


class DependencyTest(unittest.TestCase):
    def setUp(self):
        _, body = split_front_matter(SKILL.read_text(encoding="utf-8"))
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
        self.assertRegex(row, r"(?i)yes to a GitHub Pages deploy")
        self.assertRegex(row, r"(?i)no `\.git`[^|]*error")
        self.assertRegex(row, r"(?i)not the fallback")


class VerificationStateTest(unittest.TestCase):
    """D19: the skill states which phases a real deck has verified."""

    def setUp(self):
        _, body = split_front_matter(SKILL.read_text(encoding="utf-8"))
        self.text = section(body, "Verification state")
        self.flat = " ".join(self.text.split())

    def test_revise_and_publish_first_on_a_nearly_finished_presentation(self):
        self.assertRegex(
            self.flat,
            r"`revise` and `publish`[^.]*first verified on a nearly finished presentation")

    def test_names_no_personal_deck(self):
        for personal in ("bsize", "week06", "T11"):
            self.assertNotIn(personal, self.text)

    def test_grill_design_build_first_on_the_next_new_presentation(self):
        self.assertRegex(
            self.flat, r"`grill`, `design`, and `build`[^.]*first verified on the next "
                       r"new presentation")

    def test_every_phase_is_an_unverified_draft(self):
        self.assertRegex(self.flat, r"every phase is an unverified draft")
        self.assertRegex(self.flat, r"No phase has been verified on a real presentation yet")

    def test_passed_manual_checks_go_to_the_phase_files(self):
        self.assertRegex(self.flat, r"When a manual check passes, record it in its phase file")


REPO_DIRS = ("reference/", "templates/", "scripts/", "vendor/", "tests/")
MAX_LINES = 120
SHINGLE = 10  # words; a shared run this long is a restated sentence


def words(text):
    return re.findall(r"[\w`'./-]+", text.lower())


def shingles(text, n=SHINGLE):
    w = words(text)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


class WordsTest(unittest.TestCase):
    """SPEC "Words": user-facing speech says 발표 자료; old phrases still trigger."""

    def setUp(self):
        _, body = split_front_matter(SKILL.read_text(encoding="utf-8"))
        self.text = section(body, "Words")

    def test_names_the_user_facing_word_and_the_old_phrases(self):
        for word in ("발표 자료", "발표 덱", "덱 게시", "도입, 전개, 전환, 마무리"):
            with self.subTest(word=word):
                self.assertIn(word, " ".join(self.text.split()))

    def test_no_stale_week_repo_paths(self):
        # The save folder replaced the week repo (D5).
        self.assertNotIn("week repo", SKILL.read_text(encoding="utf-8"))


class RouterOnlyTest(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

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
                shared = mine & shingles(ref.read_text(encoding="utf-8"))
                self.assertFalse(shared, sorted(shared)[:3])


if __name__ == "__main__":
    unittest.main()
