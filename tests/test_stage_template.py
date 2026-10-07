"""Checks templates/stage.html against SPEC.md D9 (stage runtime, content removed).

Run: python3 -m unittest discover -s tests
"""

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "stage.html"


class Collector(HTMLParser):
    """Record every start tag as (tag, attrs) plus the text of <style>/<script>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.style = []
        self.script = []
        self._raw = None

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag in ("style", "script"):
            self._raw = tag

    def handle_endtag(self, tag):
        if tag == self._raw:
            self._raw = None

    def handle_data(self, data):
        if self._raw == "style":
            self.style.append(data)
        elif self._raw == "script":
            self.script.append(data)


def parse():
    c = Collector()
    c.feed(TEMPLATE.read_text(encoding="utf-8"))
    return c


def classes(attrs):
    return (attrs.get("class") or "").split()


class SlideStructureTest(unittest.TestCase):
    def setUp(self):
        self.doc = parse()
        self.slides = [a for t, a in self.doc.elements
                       if t == "section" and "slide" in classes(a)]

    def test_four_placeholder_slides_with_sequential_ids(self):
        self.assertEqual([a.get("id") for a in self.slides],
                         ["s1", "s2", "s3", "s4"])

    def test_every_slide_has_notes_with_target_seconds(self):
        notes = [a for t, a in self.doc.elements
                 if t == "aside" and "notes" in classes(a)]
        self.assertEqual(len(notes), len(self.slides))
        for a in notes:
            self.assertRegex(a.get("data-sec") or "", r"^\d+$")


    def test_at_least_one_slide_has_steps(self):
        steps = [a for t, a in self.doc.elements if "data-step" in a]
        self.assertTrue(steps, "no data-step element")
        for a in steps:
            self.assertRegex(a["data-step"], r"^[1-9]\d*$")


class RuntimeHooksTest(unittest.TestCase):
    """DOM ids, classes, and script hooks the stage runtime relies on."""

    def setUp(self):
        self.doc = parse()
        self.ids = {a.get("id") for _, a in self.doc.elements}
        self.cls = {c for _, a in self.doc.elements for c in classes(a)}
        self.js = "".join(self.doc.script)

    def test_chrome_elements_exist(self):
        for i in ["notesPanel", "nSlide", "nSec", "nStep", "nTotal", "nBody",
                  "progressBar", "navDots", "editToggle", "editBanner"]:
            self.assertIn(i, self.ids)
        for c in ["progress-bar", "nav-dots", "edit-toggle", "edit-banner",
                  "edit-hotzone", "keyboard-hint"]:
            self.assertIn(c, self.cls)

    def test_notes_panel_starts_hidden(self):
        panel = next(a for _, a in self.doc.elements if a.get("id") == "notesPanel")
        self.assertIn("hidden", panel)

    def test_keys_use_physical_codes(self):
        # e.code keeps E and N working with a Korean IME on (DESIGN.md runtime variants)
        for code in ["KeyN", "KeyE", "KeyS"]:
            self.assertIn(f"e.code === '{code}'", self.js)

    def test_stage_behaviors_are_wired(self):
        for hook in ["'leaving'", "hashchange", "history.replaceState",
                     "classList.toggle('on'", "localStorage", "signature",
                     "exportFile", "contenteditable"]:
            self.assertIn(hook, self.js)


def css_blocks(css, selector):
    """Bodies of top-level-or-nested rules whose selector list is exactly `selector`."""
    return [m.group(1) for m in
            re.finditer(r"(?:^|[}\s])" + re.escape(selector) + r"\s*\{([^{}]*)\}", css)]


class ViewportContractTest(unittest.TestCase):
    """Rules of vendor/frontend-slides/viewport-base.css that apply to a fixed stage."""

    def setUp(self):
        self.css = "".join(parse().style)

    def test_slide_is_exactly_one_viewport_and_never_scrolls(self):
        body = " ".join(css_blocks(self.css, ".slide"))
        self.assertRegex(body, r"height:\s*100vh")
        self.assertRegex(body, r"height:\s*100dvh")
        self.assertRegex(body, r"width:\s*100vw")
        self.assertRegex(body, r"overflow:\s*hidden")

    def test_html_body_locked(self):
        body = " ".join(css_blocks(self.css, "html, body"))
        self.assertRegex(body, r"height:\s*100%")
        self.assertRegex(body, r"overflow(-x)?:\s*hidden")

    def test_content_and_media_constraints(self):
        self.assertRegex(" ".join(css_blocks(self.css, ".slide-content")),
                         r"max-height:\s*100%")
        self.assertIn("max-height: min(50vh, 400px)",
                      " ".join(css_blocks(self.css, "img, .image-container")))
        self.assertIn("max-height: min(80vh, 700px)",
                      " ".join(css_blocks(self.css, ".card, .container, .content-box")))
        self.assertIn("minmax(min(100%, 250px), 1fr)",
                      " ".join(css_blocks(self.css, ".grid")))

    def test_height_and_width_breakpoints(self):
        for q in ["max-height: 700px", "max-height: 600px",
                  "max-height: 500px", "max-width: 600px"]:
            self.assertIn(f"@media ({q})", self.css)

    def test_very_short_viewport_hides_chrome(self):
        m = re.search(r"@media \(max-height: 600px\)(.*?)@media", self.css, re.S)
        self.assertTrue(m)
        self.assertRegex(m.group(1),
                         r"\.nav-dots, \.keyboard-hint, \.decorative\s*\{\s*display:\s*none")

    def test_reduced_motion(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.css)


class ContentRemovedTest(unittest.TestCase):
    """No week06 talk content survives (D9: content removed)."""

    WEEK06 = ["bsize", "malloc", "extend_heap", "mem_sbrk", "mdriver",
              "first_fit", "coalescing", "size_t", "unsigned int", "20MB",
              "93", "1638c7", "22,56,199", "week06", "Week 06", "WEEK 06",
              "컴파일러가 조용"]

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_no_week06_strings(self):
        for s in self.WEEK06:
            self.assertNotIn(s, self.text)

    def test_storage_key_is_not_week06(self):
        m = re.search(r"const STORE\s*=\s*([^;]+);", self.text)
        self.assertTrue(m, "no STORE key")
        self.assertNotIn("week06", m.group(1))
        self.assertNotIn("bsize", m.group(1))


class TokensTest(unittest.TestCase):
    """Every color is a :root token, so a DESIGN.md can restyle the deck in one place."""

    COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(")

    def test_colors_only_in_root_blocks(self):
        css = "".join(parse().style)
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        outside = re.sub(r":root\s*\{[^{}]*\}", "", css)
        self.assertEqual(self.COLOR.findall(outside), [])

    def test_accent_token_present(self):
        css = "".join(parse().style)
        self.assertRegex(css, r":root\s*\{[^}]*--acc:")


if __name__ == "__main__":
    unittest.main()
