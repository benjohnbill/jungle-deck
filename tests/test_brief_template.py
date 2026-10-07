"""Contract checks for reference/brief-template.md (SPEC D3-D7, issue #2).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "reference" / "brief-template.md"

REQUIRED_KEYS = {"phase", "slug", "week", "deck", "updated"}
PHASES = ["grill", "build", "revise", "publish", "done"]

# One named slot per D7 decision, in D7 order.
D7_SLOTS = [
    "Conclusion",
    "Story frame",
    "Slide theses",
    "Evidence list",
    "Accent",
    "Terms",
]


def read_template():
    return TEMPLATE.read_text(encoding="utf-8")


def skeleton(text):
    """Return the BRIEF.md skeleton: the first ```markdown fenced block."""
    m = re.search(r"^```markdown\n(.*?)^```$", text, re.S | re.M)
    if not m:
        raise AssertionError("no ```markdown skeleton block in template")
    return m.group(1)


def front_matter(body):
    """Parse a flat `key: value` front matter between leading --- lines."""
    m = re.match(r"---\n(.*?)\n---\n", body, re.S)
    if not m:
        raise AssertionError("skeleton does not start with --- front matter")
    fields = {}
    for line in m.group(1).splitlines():
        line = line.split(" #", 1)[0].strip()
        if not line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def headings(body):
    return [h.strip() for h in re.findall(r"^#{2,3} (.+)$", body, re.M)]


class BriefTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = read_template()
        self.body = skeleton(self.text)

    def test_front_matter_has_required_keys(self):
        self.assertEqual(REQUIRED_KEYS, set(front_matter(self.body)))

    def test_initial_phase_is_grill(self):
        self.assertEqual("grill", front_matter(self.body)["phase"])

    def test_all_phase_values_are_listed_in_order(self):
        self.assertIn(" → ".join(PHASES), self.text)

    def test_one_slot_per_d7_decision(self):
        hs = headings(self.body)
        for slot in D7_SLOTS:
            with self.subTest(slot=slot):
                self.assertEqual(
                    1, sum(h.startswith(slot) for h in hs), f"slot {slot!r}"
                )

    def test_one_section_per_working_phase(self):
        hs = headings(self.body)
        for phase in ["Grill", "Build", "Revise", "Publish"]:
            with self.subTest(phase=phase):
                self.assertIn(phase, hs)

    def test_skeleton_has_next_action_slot(self):
        self.assertIn("Next action", headings(self.body))

    def test_phase_change_authority_is_stated(self):
        contract = self.text.split("```markdown", 1)[0]
        self.assertRegex(contract, r"(?i)who changes `phase`")
        self.assertRegex(contract, r"(?i)student confirms")


if __name__ == "__main__":
    unittest.main()
