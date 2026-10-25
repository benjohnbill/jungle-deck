"""Checks reference/local-template.md against SPEC.md D15, D16, D20, D24.

Run: python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "reference" / "local-template.md"

# D16, in the order the spec lists them.
KEYS = ["display_name", "notes_url", "design_md", "accent", "downloads_dir",
        "python_cmd", "current_brief", "prev_brief", "pages_repo", "pages_dir",
        "pages_url_base", "card_format"]
EMPTY = {"", "-", "—", "none", "n/a"}


def section(text, heading):
    """Return the body of a '## heading' section."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        raise AssertionError(f"missing section: ## {heading}")
    return m.group(1)


def table_rows(body):
    """Return the first Markdown table in body as a list of dicts."""
    lines = []
    for l in body.splitlines():
        if l.strip().startswith("|"):
            lines.append(l.strip())
        elif lines:
            break
    if len(lines) < 3:
        raise AssertionError("no table found")
    cells = lambda l: [c.strip() for c in l.strip("|").split("|")]
    header = [h.lower() for h in cells(lines[0])]
    return [dict(zip(header, cells(l))) for l in lines[2:]]


def strip_code(cell):
    return cell.strip().strip("`").strip()


def yaml_blocks(text):
    """Key -> value maps of each ```yaml block with a --- front matter."""
    out = [{k: v.strip() for k, v in re.findall(r"(?m)^([a-z_]+):(.*)$", m.group(1))}
           for m in re.finditer(r"```yaml\n---\n(.*?)\n---\n```", text, re.S)]
    if not out:
        raise AssertionError("no ```yaml block with a --- front matter")
    return out


def flat(text):
    return re.sub(r"\s+", " ", text)


class LocalTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TEMPLATE.read_text(encoding="utf-8")
        cls.rows = table_rows(section(cls.text, "Fields"))

    def test_fields_table_has_exactly_the_d16_keys(self):
        self.assertEqual([strip_code(r["key"]) for r in self.rows], KEYS)

    def test_every_field_has_a_default_or_a_skip_meaning(self):
        for r in self.rows:
            default = strip_code(r["default"]).lower()
            skip = r["if empty"].strip().lower()
            self.assertTrue(default not in EMPTY or skip not in EMPTY,
                            f"{r['key']}: no default and no skip meaning")

    def test_every_field_says_when_it_is_asked_or_written(self):
        for r in self.rows:
            self.assertNotIn(r["asked or written"].strip().lower(), EMPTY, r["key"])

    def test_no_pages_repo_stops_at_local_html(self):
        row = next(r for r in self.rows if strip_code(r["key"]) == "pages_repo")
        self.assertIn("local html", row["if empty"].lower())

    def test_template_block_has_exactly_the_table_keys(self):
        self.assertEqual(list(yaml_blocks(self.text)[0]), KEYS)

    def test_first_run_asks_only_name_and_notes_site(self):
        body = section(self.text, "First-run questions")
        self.assertEqual([strip_code(q["writes"]) for q in table_rows(body)],
                         ["display_name", "notes_url"])
        self.assertRegex(flat(body), r'(?i)both may be `""`')

    def test_missing_versus_empty_rule(self):
        body = flat(section(self.text, "When to read and write it"))
        self.assertRegex(body, r"(?i)missing[^.]*asked once when it is first needed")
        self.assertRegex(body, r'(?i)empty value `""` is a valid answer[^.]*never asked again')

    def test_old_keys_are_ignored(self):
        body = flat(section(self.text, "Migration"))
        self.assertIn("`last_brief`", body)
        self.assertRegex(body, r"(?i)not in the Fields table[^.]*ignored")
        self.assertRegex(body, r"(?i)keeps working")

    def test_current_brief_moves_to_prev_brief_on_create(self):
        self.assertRegex(flat(self.text), r"(?i)old `current_brief`[^.]*`prev_brief`")

    def test_example_is_generic(self):
        examples = yaml_blocks(self.text)[1:]
        self.assertTrue(examples, "no example block")
        ex = examples[0]
        self.assertEqual(ex["display_name"], "홍길동")
        self.assertEqual(ex["pages_repo"], "~/my-pages")
        self.assertEqual(ex["downloads_dir"], "~/Downloads")

    def test_card_badge_says_presentation(self):
        self.assertNotIn('class="b">덱<', self.text)
        self.assertIn('class="b">발표 자료<', self.text)

    def test_local_file_is_gitignored(self):
        lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("jungle-deck.local.md", [l.strip() for l in lines])


if __name__ == "__main__":
    unittest.main()
