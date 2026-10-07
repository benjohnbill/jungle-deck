"""Contract checks for reference/grill.md and reference/context.md
(SPEC D7, D8, D15, "Shared Jungle context"; issue #7).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRILL = ROOT / "reference" / "grill.md"
CONTEXT = ROOT / "reference" / "context.md"
BRIEF = ROOT / "reference" / "brief-template.md"

# The D7 slot names, as brief-template.md spells them, in D7 order.
D7_SLOTS = [
    "Conclusion",
    "Story frame",
    "Slide theses",
    "Evidence list",
    "Accent",
    "Terms",
]


def section(text, heading):
    """Return the body of the `## heading` section, up to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise AssertionError(f"no '## {heading}' section")
    return m.group(1)


class GrillReferenceTest(unittest.TestCase):
    def setUp(self):
        self.text = GRILL.read_text(encoding="utf-8")

    def test_names_every_d7_decision_with_brief_slot_names(self):
        brief = BRIEF.read_text(encoding="utf-8")
        body = section(self.text, "The six decisions")
        positions = []
        for slot in D7_SLOTS:
            self.assertIn(slot, brief, f"brief-template.md has no slot '{slot}'")
            self.assertIn(slot, body, f"D7 slot '{slot}' missing")
            positions.append(body.index(slot))
        self.assertEqual(positions, sorted(positions), "D7 slots out of order")

    def test_context_sources_in_d8_order_with_claude_mem_optional(self):
        body = section(self.text, "Context collection")
        sources = ["git log", "README", "notes", "progress memo", "claude-mem"]
        positions = [body.find(s) for s in sources]
        self.assertNotIn(-1, positions, f"missing a source of {sources}")
        self.assertEqual(positions, sorted(positions), "sources not in D8 order")
        mem_line = next(l for l in body.splitlines() if "claude-mem" in l)
        self.assertRegex(mem_line, r"(?i)only (if|when) .*installed")

    def test_inline_grilling_fallback(self):
        body = section(self.text, "Grilling rules")
        self.assertIn("`grilling` skill", body)
        self.assertRegex(body, r"(?i)installed")
        for term in ["design tree", "frontier", "recommended answer"]:
            self.assertIn(term, body.lower(), f"fallback lacks '{term}'")

    def test_theses_are_written_by_the_student(self):
        self.assertRegex(self.text, r"(?i)the student writes (each|every|the) (slide )?thes")
        self.assertRegex(self.text, r"(?i)the agent does not (write|rephrase|edit)")

    def test_write_immediately_and_confirm_before_build(self):
        self.assertRegex(
            self.text, r"(?i)write each settled decision into `?BRIEF\.md`? immediately")
        self.assertRegex(self.text, r"`phase` to `build`")
        self.assertRegex(self.text, r"(?i)only when the student confirms")

    def test_points_to_shared_context(self):
        self.assertIn("context.md", self.text)


class ContextReferenceTest(unittest.TestCase):
    def setUp(self):
        self.text = CONTEXT.read_text(encoding="utf-8")

    def test_shared_rows_present(self):
        for row in ["Event", "Audience", "Language", "Time", "Display",
                    "Story type", "Reuse", "Deadline"]:
            self.assertRegex(self.text, rf"(?m)^\| {row}", f"row '{row}' missing")

    def test_time_is_background_not_gate(self):
        self.assertRegex(self.text, r"(?i)background, not a gate")

    def test_no_personal_rows(self):
        lower = self.text.lower()
        for banned in ["benjohnbill", "github.io", "오라버니"]:
            self.assertNotIn(banned, lower, f"personal value '{banned}' leaked")
        for row in ["Speaker", "Format"]:
            self.assertNotRegex(self.text, rf"(?m)^\| {row}", f"personal row '{row}'")
        self.assertIn("jungle-deck.local.md", self.text)


if __name__ == "__main__":
    unittest.main()
