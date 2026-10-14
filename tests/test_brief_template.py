"""Contract checks for reference/brief-template.md (SPEC D3-D7, D21, D23; issues #2, #15).

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "reference" / "brief-template.md"

REQUIRED_KEYS = {"kind", "phase", "slug", "week", "deck", "source_repo",
                 "created", "updated"}
PHASES = ["grill", "design", "build", "revise", "publish", "done"]

# One named slot per grill item that writes the BRIEF (D7), in D7 order.
GRILL_SLOTS = [
    "Context notes",
    "Metadata",
    "Story frame",
    "Title slide",
    "Slide theses",
    "Evidence list",
    "Terms",
    "Script",
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


def headings(body, level="#{2,3}"):
    return [h.strip() for h in re.findall(rf"^{level} (.+)$", body, re.M)]


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        raise AssertionError(f"missing section: ## {heading}")
    return m.group(1)


def flat(text):
    return re.sub(r"\s+", " ", text)


class BriefTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = read_template()
        self.body = skeleton(self.text)
        self.contract = self.text.split("```markdown", 1)[0]

    def test_front_matter_has_required_keys(self):
        self.assertEqual(REQUIRED_KEYS, set(front_matter(self.body)))

    def test_kind_marks_the_file(self):
        self.assertEqual("jungle-deck", front_matter(self.body)["kind"])

    def test_initial_phase_is_grill(self):
        self.assertEqual("grill", front_matter(self.body)["phase"])

    def test_all_phase_values_are_listed_in_order(self):
        self.assertIn(" → ".join(PHASES), self.text)

    def test_one_slot_per_grill_item_in_order(self):
        hs = headings(section(self.body, "Grill"), "###")
        for slot in GRILL_SLOTS:
            with self.subTest(slot=slot):
                self.assertEqual(1, sum(h.startswith(slot) for h in hs), f"slot {slot!r}")
        order = [next(i for i, h in enumerate(hs) if h.startswith(s)) for s in GRILL_SLOTS]
        self.assertEqual(order, sorted(order))

    def test_one_section_per_working_phase(self):
        hs = headings(self.body, "##")
        for phase in ["Grill", "Design", "Build", "Revise", "Publish"]:
            with self.subTest(phase=phase):
                self.assertIn(phase, hs)

    def test_design_section_records_source_tokens_accent(self):
        design = section(self.body, "Design")
        for item in ["Source", "Tokens", "Accent", "Accent key"]:
            self.assertRegex(design, rf"(?m)^- {item}:")

    def test_story_frame_asks_structure_and_opening(self):
        frame = flat(re.search(r"^### Story frame\n(.*?)^###", self.body, re.S | re.M).group(1))
        self.assertIn("오프닝 → 도입 → 전개 → 전환 → 마무리", frame)
        self.assertIn("증상 → 증거 → 원인", frame)
        self.assertRegex(frame, r"(?i)opening")
        self.assertNotRegex(self.text, r"[起承轉結]")

    def test_values_are_placeholders_not_a_real_deck(self):
        fm = front_matter(self.body)
        self.assertEqual("<slug>", fm["slug"])
        self.assertEqual("<slug>.html", fm["deck"])
        for k in ["source_repo", "created", "updated"]:
            self.assertRegex(fm[k], r"^<[^>]+>$", k)
        self.assertIn("# BRIEF — <slug>", self.body)

    def test_no_week_repo_layout(self):
        self.assertNotIn("week repo", self.text.lower())
        self.assertNotIn("study/<", self.text)

    def test_deck_is_relative_to_the_brief_folder(self):
        self.assertRegex(flat(self.contract), r"(?i)`deck` is relative to the save folder")

    def test_week_is_optional_and_never_asked(self):
        c = flat(self.contract)
        self.assertIn(r"week\d+", c)
        self.assertRegex(c, r"(?i)never ask")

    def test_skeleton_has_next_action_slot(self):
        self.assertIn("Next action", headings(self.body))

    def test_phase_change_authority_is_stated(self):
        self.assertRegex(self.contract, r"(?i)who changes `phase`")
        self.assertRegex(self.contract, r"(?i)student confirms")

    def test_proposal_rule_replaces_student_writes(self):
        c = flat(self.text)
        self.assertRegex(c, r"(?i)pick or rewrite")
        self.assertNotRegex(c, r"(?i)student writes (each|the slide)")


class SaveFolderTest(unittest.TestCase):
    def setUp(self):
        self.body = flat(section(read_template(), "Save folder"))

    def test_asks_where_to_save_with_the_default(self):
        self.assertIn("이번 주 발표 자료를 어디에 저장할까요?", self.body)
        self.assertIn("<current directory>/<slug>/", self.body)

    def test_folder_contents(self):
        for item in ["BRIEF.md", "<slug>.html", "<slug>.assets/", "evidence/", ".gitignore"]:
            self.assertIn(item, self.body)

    def test_kind_line_defers_to_how_to_resume(self):
        # "How to resume" step 1 is the one source for what counts as a BRIEF;
        # it also accepts the old format (D23).
        line = next(l for l in self.body.split(" - ") if l.startswith("`kind: jungle-deck`"))
        self.assertNotRegex(line, r"(?i)\bonly a file with this line\b")
        self.assertIn("old format", line)
        self.assertIn('"How to resume"', line)


class ResumeTest(unittest.TestCase):
    def setUp(self):
        self.body = flat(section(read_template(), "How to resume"))

    def test_search_order(self):
        order = [self.body.find(s) for s in
                 ["`<cwd>/BRIEF.md`", "`<cwd>/*/BRIEF.md`", "`current_brief`"]]
        self.assertNotIn(-1, order)
        self.assertEqual(order, sorted(order))

    def test_kind_or_the_old_format_counts(self):
        # D5 marks a BRIEF by `kind`; D23 still recognizes the old three keys
        step1 = self.body[:self.body.index(" 2. ")]
        self.assertIn("`kind: jungle-deck`", step1)
        for k in ["`phase:`", "`slug:`", "`deck:`"]:
            self.assertIn(k, step1)


class MigrationTest(unittest.TestCase):
    """D23: an old-format BRIEF.md."""

    def setUp(self):
        self.body = flat(section(read_template(), "Migration from the old format"))

    def test_recognized_by_three_keys(self):
        for k in ["`phase:`", "`slug:`", "`deck:`"]:
            self.assertIn(k, self.body)

    def test_adds_kind_and_created(self):
        self.assertIn("`kind: jungle-deck`", self.body)
        self.assertRegex(self.body, r"(?i)`created`.*first commit.*else (the )?`updated`")

    def test_grill_adds_new_slots_as_tbd(self):
        self.assertIn("`phase: grill`", self.body)
        for slot in ["Metadata", "Story frame", "Title slide", "Script", "Design"]:
            self.assertIn(slot, self.body)
        self.assertIn("`TBD`", self.body)
        self.assertRegex(self.body, r"(?i)`Conclusion`[^.]*title slide")

    def test_build_or_later_changes_nothing_else(self):
        self.assertRegex(self.body, r"(?i)`build` or later[^.]*nothing else")


if __name__ == "__main__":
    unittest.main()
