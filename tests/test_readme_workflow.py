"""Contract checks for the README workflow and troubleshooting tables
(SPEC D3, D26; issue #23).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

PHASES = ("grill", "design", "build", "revise", "publish")


def section(text, heading, level="##"):
    m = re.search(rf"(?ms)^{level} {re.escape(heading)}\b[^\n]*\n(.*?)(?=^#{{2,{len(level)}}} |\Z)",
                  text)
    if not m:
        raise AssertionError(f"README has no '{level} {heading}' section")
    return m.group(1)


def flat_text(text):
    return " ".join(text.split())


def table_rows(text):
    lines = [l for l in text.splitlines() if l.startswith("|")]
    return [l for l in lines[2:] if not re.match(r"^\|[-| ]+\|$", l)]


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow = section(README, "Workflow")

    def test_names_the_six_phases_in_order(self):
        self.assertIn("`grill → design → build → revise → publish → done`", README)

    def test_one_table_per_phase_with_asks_and_decides(self):
        for phase in PHASES:
            with self.subTest(phase=phase):
                body = section(self.workflow, phase, "###")
                self.assertIn("| The skill does or asks | You decide |", body)
                self.assertTrue(table_rows(body), f"{phase}: empty table")

    def test_phase_tables_follow_d3_order(self):
        # `done` has no table: nothing runs there.
        order = [self.workflow.find(f"### {p} ") for p in PHASES]
        self.assertNotIn(-1, order, order)
        self.assertEqual(order, sorted(order))

    def test_keys_name_the_size_buttons(self):
        # #31: in edit mode, Tab opens the size buttons.
        keys = flat_text(self.workflow[self.workflow.index("Keys in the page"):])
        self.assertRegex(keys[:300], r"`Tab`.*(size|크기)")

    def test_user_facing_word_is_the_new_one(self):
        # SPEC "Words": the README offers the new phrases; the old ones only as "still work".
        self.assertIn("발표 자료 만들자", README)
        self.assertIn("발표 자료 게시", README)
        for para in README.split("\n\n"):
            if "발표 덱" in para or "덱 게시" in para:
                self.assertIn("still work", " ".join(para.split()))


class TroubleshootingTest(unittest.TestCase):
    def setUp(self):
        self.rows = table_rows(section(README, "Troubleshooting"))

    def test_d26_rows(self):
        for symptom in ("localhostForwarding=false", "서버가 꺼져 있어요", "`Monitor`"):
            with self.subTest(symptom=symptom):
                self.assertTrue(any(symptom in r for r in self.rows), symptom)

    def test_each_row_has_symptom_cause_fix(self):
        for row in self.rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(len(cells), 3, row)
            self.assertTrue(all(cells), row)


if __name__ == "__main__":
    unittest.main()
