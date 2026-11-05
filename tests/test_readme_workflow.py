"""Contract checks for the README landing page and docs/MANUAL.md
(SPEC D3, D26; issue #23).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
MANUAL = (ROOT / "docs" / "MANUAL.md").read_text(encoding="utf-8")
STAGE = (ROOT / "templates" / "stage.html").read_text(encoding="utf-8")
SKILL_SOURCES = [ROOT / "SKILL.md", *sorted((ROOT / "reference").glob("*.md")),
                 ROOT / "templates" / "stage.html", ROOT / "scripts" / "serve.py"]

PHASES = ("grill", "design", "build", "revise", "publish")


def section(text, heading, level="##"):
    m = re.search(rf"(?ms)^{level} {re.escape(heading)}\b[^\n]*\n(.*?)(?=^#{{2,{len(level)}}} |\Z)",
                  text)
    if not m:
        raise AssertionError(f"no '{level} {heading}' section")
    return m.group(1)


def flat_text(text):
    return " ".join(text.split())


def without_backticks(text):
    return flat_text(text.replace("`", ""))


def table_rows(text):
    lines = [l for l in text.splitlines() if l.startswith("|")]
    return [l for l in lines[2:] if not re.match(r"^\|[-| ]+\|$", l)]


class LandingPageTest(unittest.TestCase):
    def test_names_the_six_phases_in_order(self):
        self.assertIn("`grill → design → build → revise → publish → done`", README)

    def test_points_at_the_manual(self):
        self.assertIn("`docs/MANUAL.md`", README)

    def test_user_facing_word_is_the_new_one(self):
        # SPEC "Words": the docs offer the new phrases; the old ones only as an old form.
        self.assertIn("`/jungle-deck`", README)
        self.assertIn("발표 자료 게시", README)
        for doc in (README, MANUAL):
            for para in doc.split("\n\n"):
                if re.search(r"(?<!인)덱", para):  # 인덱스 is another word
                    self.assertIn("예전 표현", para)

    def test_says_which_example_is_the_closest(self):
        row = next(l for l in README.splitlines() if "deck-Y.html" in l)
        self.assertIn("가장 가까워요", row)

    def test_example_links_come_before_the_install_steps(self):
        start = README.index("## 시작하기")
        for deck in ("deck-Y.html", "deck-X.html"):
            self.assertLess(README.index(deck), start, deck)


class QuotedStringsTest(unittest.TestCase):
    """The docs are a hand copy of what the skill says. A copy must not drift."""

    def test_quoted_korean_strings_exist_in_the_skill(self):
        source = " ".join(without_backticks(p.read_text(encoding="utf-8")) for p in SKILL_SOURCES)
        for doc in (README, MANUAL):
            quoted = re.findall(r'"([^"\n]*[가-힣][^"\n]*)"', doc)
            self.assertTrue(quoted)
            for string in quoted:
                with self.subTest(string=string):
                    self.assertIn(without_backticks(string), source)


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow = section(MANUAL, "단계별 흐름")

    def test_one_table_per_phase_with_asks_and_decides(self):
        for phase in PHASES:
            with self.subTest(phase=phase):
                body = section(self.workflow, phase, "###")
                self.assertIn("| 스킬이 하는 일과 묻는 말 | 내가 정할 것 |", body)
                self.assertTrue(table_rows(body), f"{phase}: empty table")

    def test_phase_tables_follow_d3_order(self):
        # `done` has no table: nothing runs there.
        order = [self.workflow.find(f"### {p} ") for p in PHASES]
        self.assertNotIn(-1, order, order)
        self.assertEqual(order, sorted(order))

    def test_grill_asks_first_and_build_checks_once(self):
        # D7, D8, D9 (2026-10-25): the student leads; one layout check.
        grill = section(self.workflow, "grill", "###")
        rows = table_rows(grill)
        self.assertIn("이번 주에 발표하고 싶은 아이템", rows[0])
        self.assertNotRegex(rows[0], r"커밋")
        self.assertIn("scripts/check_layout.py", section(self.workflow, "build", "###"))
        self.assertIn("새 세션", section(self.workflow, "design", "###"))

    def test_figures_are_explained(self):
        # reference/grill.md asks for the Show line. Edit mode cannot change SVG text.
        self.assertIn("`Show`", section(self.workflow, "grill", "###"))
        self.assertIn("도식", section(self.workflow, "build", "###"))
        self.assertIn("도식 안의 글자를 고칠 수 없어요", section(self.workflow, "revise", "###"))

    def test_keys_name_the_size_buttons(self):
        # #31: in edit mode, Tab opens the size buttons.
        keys = flat_text(self.workflow[self.workflow.index("페이지 단축키"):])
        self.assertRegex(keys[:300], r"`Tab`.*크기")


class TroubleshootingTest(unittest.TestCase):
    def setUp(self):
        self.rows = table_rows(section(MANUAL, "문제 해결"))

    def test_d26_rows(self):
        for symptom in ("localhostForwarding=false", "서버가 꺼져 있어요", "`Monitor`"):
            with self.subTest(symptom=symptom):
                self.assertTrue(any(symptom in r for r in self.rows), symptom)

    def test_page_notice_rows(self):
        # #32: each notice the page can show about the skill's edits has a row.
        for symptom, fixes in (("에이전트 수정 뒤 내 저장 문구가 바뀌었어요", ['"복원"', '"그대로 두기"']),
                               ("글이 상자를 넘쳐요", ["레이아웃 조정", "내 글과 크기를 그대로"]),
                               ("에이전트가 슬라이드를 지웠어요", ["일부러 지웠는지", "되돌려요"])):
            with self.subTest(symptom=symptom):
                self.assertIn(symptom, STAGE)
                row = next((r for r in self.rows if symptom in r.split("|")[1]), None)
                self.assertIsNotNone(row, symptom)
                fix = row.split("|")[3]
                for f in fixes:
                    self.assertIn(f, fix)

    def test_each_row_has_symptom_cause_fix(self):
        for row in self.rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(len(cells), 3, row)
            self.assertTrue(all(cells), row)


if __name__ == "__main__":
    unittest.main()
