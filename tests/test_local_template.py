"""Checks reference/local-template.md against SPEC.md D15 and D16.

Run: python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "reference" / "local-template.md"

# D16, in the order the spec lists them.
REQUIRED_FIELDS = [
    "display name",
    "week-repo root",
    "Pages repo path",
    "Pages URL base",
    "card format",
    "DESIGN.md path",
    "preferred accent",
]
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


def front_matter_keys(text):
    """Keys of the YAML front matter inside the first ```yaml block."""
    m = re.search(r"```yaml\n---\n(.*?)\n---\n```", text, re.S)
    if not m:
        raise AssertionError("no ```yaml block with a --- front matter")
    return [re.match(r"([a-z_]+):", l).group(1)
            for l in m.group(1).splitlines() if re.match(r"[a-z_]+:", l)]


class LocalTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TEMPLATE.read_text(encoding="utf-8")
        cls.rows = table_rows(section(cls.text, "Fields"))

    def test_every_d16_field_has_a_row(self):
        names = [r["field"].lower() for r in self.rows]
        for field in REQUIRED_FIELDS:
            self.assertIn(field.lower(), names)

    def test_keys_are_unique_snake_case(self):
        keys = [strip_code(r["key"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))
        for k in keys:
            self.assertRegex(k, r"^[a-z][a-z0-9_]*$")

    def test_every_field_has_a_default_or_a_skip_meaning(self):
        for r in self.rows:
            default = strip_code(r["default"]).lower()
            skip = r["if empty"].strip().lower()
            self.assertTrue(default not in EMPTY or skip not in EMPTY,
                            f"{r['key']}: no default and no skip meaning")

    def test_no_pages_repo_stops_at_local_html(self):
        row = next(r for r in self.rows if r["field"].lower() == "pages repo path")
        self.assertIn("local html", row["if empty"].lower())

    def test_template_block_has_exactly_the_table_keys(self):
        keys = [strip_code(r["key"]) for r in self.rows]
        self.assertEqual(front_matter_keys(self.text), keys)

    def test_first_run_questions_each_name_a_key_and_a_default(self):
        rows = table_rows(section(self.text, "First-run questions"))
        keys = {strip_code(r["key"]) for r in self.rows}
        self.assertTrue(0 < len(rows) <= 7)
        for q in rows:
            self.assertIn(strip_code(q["writes"]), keys)
            self.assertNotIn(q["default answer"].strip().lower(), EMPTY)

    def test_author_values_are_not_defaults(self):
        for r in self.rows:
            self.assertNotIn("benjohnbill", r["default"])

    def test_local_file_is_gitignored(self):
        lines = (ROOT / ".gitignore").read_text().splitlines()
        self.assertIn("jungle-deck.local.md", [l.strip() for l in lines])


if __name__ == "__main__":
    unittest.main()
