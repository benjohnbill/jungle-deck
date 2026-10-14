"""Contract checks for reference/grill.md and reference/context.md
(SPEC D7, D8, D15, D22, "Shared Jungle context"; issues #7, #19).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRILL = ROOT / "reference" / "grill.md"
CONTEXT = ROOT / "reference" / "context.md"
BRIEF = ROOT / "reference" / "brief-template.md"

# The grill slots, as brief-template.md spells them, in D7 round order.
D7_SLOTS = [
    "Metadata",
    "Story frame",
    "Title slide and closing line",
    "Slide theses",
    "Evidence list",
    "Terms to define on screen",
    "Script",
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

    def test_rounds_follow_d7_order_with_brief_slot_names(self):
        brief = BRIEF.read_text(encoding="utf-8")
        body = section(self.text, "Rounds")
        positions = []
        for slot in D7_SLOTS:
            self.assertIn(f"### {slot}", brief, f"brief-template.md has no slot '{slot}'")
            self.assertIn(slot, body, f"D7 slot '{slot}' missing")
            positions.append(body.index(slot))
        self.assertEqual(positions, sorted(positions), "D7 slots out of order")
        # (1) collection comes first, (9) the design question comes last.
        self.assertLess(body.index("Context collection"), positions[0])
        self.assertGreater(body.index("이 내용으로 디자인을 정할까요?"), positions[-1])

    def test_metadata_round_shares_the_check_in(self):
        body = section(self.text, "Rounds")
        for item in ["What to present", "Why", "take away", "Slide count",
                     "맥락 기준 추천"]:
            self.assertIn(item, body, f"metadata round lacks '{item}'")
        self.assertRegex(body, r"(?i)same round")
        self.assertRegex(body, r"(?i)collect again.*re-propose")
        self.assertRegex(body, r"before recording any metadata")

    def test_story_frame_two_questions(self):
        body = section(self.text, "Rounds")
        self.assertIn("오프닝 → 도입 → 전개 → 전환 → 마무리", body)
        self.assertIn("증상 → 증거 → 원인", body)
        self.assertIn("prev_brief", body)
        self.assertRegex(body, r"(?i)fixes no slide count")

    def test_script_is_optional_and_guidance_only(self):
        body = section(self.text, "Rounds")
        self.assertIn("발표 스크립트를 먼저 만들까요?", body)
        self.assertIn("600–700", body)
        self.assertIn("없음 — build가 가벼운 노트를 씀", body)

    def test_context_sources_in_d8_order_with_claude_mem_optional(self):
        body = section(self.text, "Context collection")
        sources = ["source_repo", "--author", "notes_url", "`gh`",
                   "REST API", "parent", "claude-mem"]
        positions = [body.find(s) for s in sources]
        self.assertNotIn(-1, positions, f"missing a source of {sources}")
        self.assertEqual(positions, sorted(positions), "sources not in D8 order")
        mem_line = next(l for l in body.splitlines() if "claude-mem" in l)
        self.assertRegex(mem_line, r"(?i)only (if|when) .*installed")

    def test_log_window_from_prev_brief_else_seven_days(self):
        body = section(self.text, "Context collection")
        self.assertRegex(body, r"(?s)`created`.*`prev_brief`")
        self.assertRegex(body, r"(?i)last 7 days")
        self.assertIn("60 requests per hour", body)

    def test_check_in_message_wording(self):
        body = section(self.text, "Context collection")
        for line in ["이 로컬 저장소를 기준으로 보면 될까요?", "본인 커밋만 봤어요"]:
            self.assertIn(line, body)
        self.assertRegex(body, r"(?i)could not (be )?read")
        self.assertRegex(body, r"(?i)team log")
        self.assertRegex(body, r"(?i)paste or export")

    def test_inline_grilling_fallback(self):
        body = section(self.text, "Grilling rules")
        self.assertIn("`grilling` skill", body)
        self.assertRegex(body, r"(?i)installed")
        for term in ["design tree", "frontier", "recommended answer"]:
            self.assertIn(term, body.lower(), f"fallback lacks '{term}'")

    def test_proposal_rule_replaces_the_thesis_ban(self):
        self.assertIn("Proposal rule", self.text)
        self.assertRegex(self.text, r"(?i)1[–-]3 candidates or a draft")
        self.assertRegex(self.text, r"recommend one")
        self.assertRegex(self.text, r"(?i)student's pick or rewrite")
        self.assertNotRegex(self.text, r"(?i)the student writes (each|every|the) (slide )?thes")
        self.assertNotRegex(self.text, r"(?i)do not offer a thesis")

    def test_write_immediately_and_confirm_before_design(self):
        self.assertRegex(
            self.text, r"Write each settled slot into `BRIEF\.md` immediately")
        self.assertRegex(self.text, r"`phase` to `design`")
        self.assertNotRegex(self.text, r"`phase` to `build`")
        self.assertRegex(self.text, r"(?i)only when the student confirms")

    def test_evidence_runs_in_source_repo(self):
        self.assertRegex(self.text, r"(?i)re-run.*in `source_repo`")
        self.assertIn("evidence/", self.text)

    def test_points_to_shared_context(self):
        self.assertIn("context.md", self.text)


class ContextReferenceTest(unittest.TestCase):
    def setUp(self):
        self.text = CONTEXT.read_text(encoding="utf-8")

    def test_shared_rows_present(self):
        for row in ["Event", "Audience", "Language", "Time", "Display",
                    "Story type", "Reuse"]:
            self.assertRegex(self.text, rf"(?m)^\| {row}", f"row '{row}' missing")

    def test_no_personal_theme_rule(self):
        self.assertNotRegex(self.text, r"(?i)light theme")

    def test_slide_count_is_a_soft_guideline(self):
        self.assertRegex(self.text, r"(?i)6 ± 2 slides \(a suggestion, not a rule\)")
        self.assertNotRegex(self.text, r"(?i)aim for \d|± 4")

    def test_general_across_weeks(self):
        # D22: C weeks, Pintos weeks, later Python and AI weeks.
        self.assertRegex(self.text, r"(?m)^\| Evidence")
        self.assertRegex(self.text, r"(?i)test results or terminal logs")
        for c_only in ["studies C", "general C", "gcc", "gdb", "valgrind"]:
            self.assertNotIn(c_only, self.text, f"C-only wording '{c_only}'")

    def test_time_is_background_not_gate(self):
        self.assertRegex(self.text, r"(?i)background, not a gate")

    def test_no_personal_rows(self):
        lower = self.text.lower()
        for banned in ["github.io", "오라버니"]:  # the author name: test_author_values
            self.assertNotIn(banned, lower, f"personal value '{banned}' leaked")
        for row in ["Speaker", "Format", "Deadline"]:
            self.assertNotRegex(self.text, rf"(?m)^\| {row}", f"personal row '{row}'")
        self.assertIn("jungle-deck.local.md", self.text)


class WordingTest(unittest.TestCase):
    """SPEC "Words": user-facing Korean says 발표 자료; no Hanja story stages."""

    def test_no_deck_word_or_hanja_in_korean(self):
        for path in [GRILL, CONTEXT]:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("덱", text)
                self.assertNotRegex(text, r"[起承轉結]")


if __name__ == "__main__":
    unittest.main()
