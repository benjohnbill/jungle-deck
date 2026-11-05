"""Contract checks for cases/ (SPEC D28), through tools/check_cases.py.

Run: python3 -m unittest discover -s tests
"""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_cases", ROOT / "tools" / "check_cases.py")
check_cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_cases)

GOOD_DESIGN = """---
name: Sample
description: A sample.
colors:
  canvas: "#ffffff"
  ink: "#000000"
  primary: "#ff0000"
  ink-mute: "#666666"
  surface: "#eeeeee"
  hairline: "#dddddd"
typography:
  body: { fontFamily: Sans }
---

## The one rule
## Slides
## CSS to add
## Figure vocabulary

**Node.** A box.

```html
<rect id="SLOT-a" fill="var(--paper)"/>
```

## Do not
"""


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RealCasesTest(unittest.TestCase):
    def test_every_case_and_the_index_pass(self):
        self.assertEqual(check_cases.check_all(), [])

    def test_the_six_talks_are_listed(self):
        rows = check_cases.INDEX_ROW.findall(read("cases/INDEX.md"))
        self.assertEqual([r[0] for r in rows], [
            "week04-array-in-c", "week05-oop-in-c", "week06-bsize-cast",
            "week07-circular-list", "week08-p2-team-workflow", "week09-clean-code"])

    def test_talks_with_a_brief_ship_a_public_record(self):
        for case in ("week07-circular-list", "week08-p2-team-workflow", "week09-clean-code"):
            self.assertTrue((ROOT / "cases" / case / "BRIEF.md").is_file(), case)


class CheckerCatchesTest(unittest.TestCase):
    """A check that no input could fail is not a check."""

    def design_problems(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(text, encoding="utf-8")
            return check_cases.check_design(path)

    def test_good_design_passes(self):
        self.assertEqual(self.design_problems(GOOD_DESIGN), [])

    def test_raw_color_in_a_snippet(self):
        self.assertTrue(self.design_problems(GOOD_DESIGN.replace("var(--paper)", "#ffffff")))

    def test_id_without_slot_prefix(self):
        self.assertTrue(self.design_problems(GOOD_DESIGN.replace("SLOT-a", "fig-a")))

    def test_small_svg_text(self):
        self.assertTrue(self.design_problems(GOOD_DESIGN.replace('fill="var(--paper)"', 'font-size="9"')))

    def test_stacked_svg_frames(self):
        self.assertTrue(self.design_problems(GOOD_DESIGN.replace("<rect id=\"SLOT-a\"", "<svg class=\"fr\"")))

    def test_missing_token(self):
        self.assertTrue(self.design_problems(GOOD_DESIGN.replace("  hairline: \"#dddddd\"\n", "")))

    def test_missing_part(self):
        self.assertTrue(self.design_problems(GOOD_DESIGN.replace("**Node.** A box.", "A box.")))

    def test_live_brief_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BRIEF.md"
            path.write_text("---\nphase: build\nslug: a\n---\n", encoding="utf-8")
            self.assertEqual(len(check_cases.check_brief(path)), 2)

    def test_name_scan_finds_a_latin_token_and_hangul_with_a_particle(self):
        hashes = {check_cases.digest("zorblax"), check_cases.digest("홍길동")}
        text = "clean line\nby ZORBLAX-repo\n작성자 홍길동이 만듦\nzorblaxes stay"
        self.assertEqual(check_cases.name_hits(text, hashes), [2, 3])


class ReadOnRequestTest(unittest.TestCase):
    def test_design_gates_cases_on_the_students_request(self):
        design = read("reference/design.md")
        section = design.split("## Cases\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Do not offer cases first", section)
        steps = design.split("## getdesign.md references", 1)[0]
        self.assertNotIn("cases/", steps)

    def test_grill_and_context_do_not_route_to_cases(self):
        for path in ("reference/grill.md", "reference/context.md"):
            self.assertNotIn("cases/", read(path), path)

    def test_build_reads_a_case_only_through_the_design_section(self):
        build = read("reference/build.md")
        self.assertEqual(len(re.findall(r"cases/<case>/DESIGN\.md", build)), 1)
        self.assertNotIn("BRIEF.md`, read", build.split("cases/<case>", 1)[1][:80])

    def test_brief_template_records_borrowed_parts(self):
        self.assertIn("- Figures from:", read("reference/brief-template.md"))

    def test_publish_never_writes_back_to_a_case(self):
        self.assertIn("Never edit a file under `cases/`", read("reference/publish.md"))


if __name__ == "__main__":
    unittest.main()
