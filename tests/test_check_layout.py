"""Tests for scripts/check_layout.py: overflow and overlap per section (SPEC D9, D15).

Run: python3 -m unittest discover -s tests
Parsing, the report, and browser detection run on any host. The render tests
need a Chromium-family browser and are skipped without one.
"""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_layout", ROOT / "scripts" / "check_layout.py")
check_layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_layout)

TEMPLATE = (ROOT / "templates" / "stage.html").read_text(encoding="utf-8")
BROWSER = check_layout.find_browser()


def dump(data):
    """A --dump-dom output that holds the measuring script's record."""
    text = json.dumps(data).replace("<", "\\u003c")
    return ('<html><body><section class="slide" id="s1"></section>'
            '<script type="application/json" id="jd-layout">' + text + "</script></body></html>")


def clean(*ids):
    return {"viewport": [1280, 720], "sections": [{"id": i, "overflow": [], "overlap": []} for i in ids]}


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = check_layout.main(argv)
    return code, out.getvalue(), err.getvalue()


class ParseDump(unittest.TestCase):
    def test_reads_the_record_out_of_the_dumped_page(self):
        data = {"viewport": [1280, 720], "sections": [
            {"id": "s1", "overflow": ['p "a </script> b"'], "overlap": [["h1", "svg"]]}]}
        self.assertEqual(check_layout.parse_dump(dump(data)), data)

    def test_a_page_without_the_record_is_an_error(self):
        with self.assertRaises(check_layout.LayoutError):
            check_layout.parse_dump("<html><body></body></html>")

    def test_an_error_record_is_an_error(self):
        with self.assertRaises(check_layout.LayoutError) as cm:
            check_layout.parse_dump(dump({"error": "no stage overflow check"}))
        self.assertIn("no stage overflow check", str(cm.exception))


class Report(unittest.TestCase):
    def test_clean_page_one_ok_line_per_section_and_exit_0(self):
        lines, code = check_layout.report([("1280x720", clean("s1", "s2")), ("1920x1080", clean("s1", "s2"))])
        self.assertEqual(code, 0)
        self.assertEqual(lines[:2], ["s1  ok", "s2  ok"])
        self.assertEqual(len(lines), 3)
        self.assertIn("1280x720", lines[2])
        self.assertIn("1920x1080", lines[2])

    def test_overflow_names_the_size_and_the_box_and_exits_1(self):
        small = clean("s1", "s2")
        small["sections"][1]["overflow"] = ['p.punch "long line"']
        lines, code = check_layout.report([("1280x720", small), ("1920x1080", clean("s1", "s2"))])
        self.assertEqual(code, 1)
        self.assertEqual(lines[0], "s1  ok")
        self.assertIn("overflow", lines[1])
        self.assertIn("1280x720", lines[1])
        self.assertNotIn("1920x1080", lines[1])
        self.assertIn('p.punch "long line"', lines[1])
        self.assertIn("s2", lines[-1])

    def test_overlap_names_both_boxes(self):
        big = clean("s1")
        big["sections"][0]["overlap"] = [['h1 "title"', "svg"]]
        lines, code = check_layout.report([("1920x1080", big)])
        self.assertEqual(code, 1)
        self.assertIn("overlap", lines[0])
        self.assertIn('h1 "title"', lines[0])
        self.assertIn("svg", lines[0])


class FindBrowser(unittest.TestCase):
    def test_linux_finds_chrome_on_path(self):
        which = {"google-chrome": "/usr/bin/google-chrome"}.get
        self.assertEqual(check_layout.find_browser("Linux", {}, lambda p: False, which), "/usr/bin/google-chrome")

    def test_linux_finds_chromium_when_chrome_is_absent(self):
        which = {"chromium": "/usr/bin/chromium"}.get
        self.assertEqual(check_layout.find_browser("Linux", {}, lambda p: False, which), "/usr/bin/chromium")

    def test_macos_finds_the_app_bundle(self):
        app = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.assertEqual(check_layout.find_browser("Darwin", {}, lambda p: p == app, lambda n: None), app)

    def test_windows_finds_edge_under_program_files(self):
        env = {"PROGRAMFILES(X86)": r"C:\Program Files (x86)"}
        edge = str(PureWindowsPath(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"))
        self.assertEqual(check_layout.find_browser("Windows", env, lambda p: p == edge, lambda n: None), edge)

    def test_wsl_without_a_linux_browser_finds_windows_edge(self):
        edge = "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
        self.assertEqual(check_layout.find_browser("Linux", {}, lambda p: p == edge, lambda n: None, wsl=True), edge)
        self.assertIsNone(check_layout.find_browser("Linux", {}, lambda p: p == edge, lambda n: None, wsl=False))

    def test_none_when_nothing_is_installed(self):
        for system in ("Linux", "Darwin", "Windows"):
            self.assertIsNone(check_layout.find_browser(system, {"PROGRAMFILES": r"C:\Program Files"},
                                                        lambda p: False, lambda n: None))


class Main(unittest.TestCase):
    def test_no_browser_skips_with_one_line_and_exit_3(self):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "deck.html"
            page.write_text(TEMPLATE, encoding="utf-8")
            with unittest.mock.patch.object(check_layout, "find_browser", return_value=None):
                code, out, _ = run_main([str(page)])
        self.assertEqual(code, 3)
        self.assertEqual(out.strip().splitlines(), [out.strip()])
        self.assertTrue(out.startswith("skipped: no headless browser"))

    def test_missing_page_exits_2(self):
        code, _, err = run_main(["/nonexistent/deck.html"])
        self.assertEqual(code, 2)
        self.assertIn("deck.html", err)

    def test_help_names_the_exit_codes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            check_layout.main(["--help"])
        self.assertEqual(cm.exception.code, 0)
        for text in ("usage: check_layout.py", "--browser", "1280x720", "1920x1080", "exit"):
            self.assertIn(text, out.getvalue())


def page_with(*edits):
    """The template with each (old, new) replacement applied once."""
    html = TEMPLATE
    for old, new in edits:
        assert old in html, old
        html = html.replace(old, new, 1)
    return html


TAKEAWAY = '<p class="hint">덧붙일 근거나 조건 한 줄</p>'
TITLE = '<h1>발표 제목을 <em>한 줄</em>로</h1>'
LONG = "".join("<p>넘치는 줄 %d: 이 슬라이드에는 글이 너무 많아서 상자를 넘어간다</p>\n" % i for i in range(40))
COVER = '<svg style="position:absolute;inset:0;width:100%;height:100%"></svg>'


WSL_EDGE = "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"


@unittest.skipUnless(check_layout.is_wsl() and os.path.isfile(WSL_EDGE), "not WSL with Windows Edge")
class WindowsBrowserFromWsl(unittest.TestCase):
    def test_windows_edge_measures_a_page_in_the_wsl_filesystem(self):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "deck.html"
            page.write_text(page_with((TAKEAWAY, TAKEAWAY + LONG)), encoding="utf-8")
            code, out, err = run_main([str(page), "--browser", WSL_EDGE])
            self.assertEqual(os.listdir(d), ["deck.html"], "the measuring copy is removed")
        self.assertEqual(code, 1, out + err)
        self.assertTrue(out.splitlines()[2].startswith("s3  overflow"), out)


@unittest.skipUnless(BROWSER, "no Chromium-family browser")
class Render(unittest.TestCase):
    def check(self, html):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "deck.html"
            page.write_text(html, encoding="utf-8")
            code, out, err = run_main([str(page)])
            self.assertEqual(os.listdir(d), ["deck.html"], "the measuring copy is removed")
        return code, out.splitlines(), err

    def test_the_template_is_clean(self):
        code, lines, err = self.check(TEMPLATE)
        self.assertEqual(code, 0, "\n".join(lines) + err)
        self.assertEqual(lines[:4], ["s1  ok", "s2  ok", "s3  ok", "s4  ok"])

    def test_too_much_text_on_one_slide_is_overflow_on_that_slide_only(self):
        code, lines, _ = self.check(page_with((TAKEAWAY, TAKEAWAY + LONG)))
        self.assertEqual(code, 1)
        self.assertEqual([l for l in lines[:4] if l.endswith("  ok")], ["s1  ok", "s2  ok", "s4  ok"])
        self.assertTrue(lines[2].startswith("s3  overflow"), lines[2])

    def test_a_box_drawn_over_the_title_is_an_overlap(self):
        code, lines, _ = self.check(page_with((TITLE, TITLE + COVER)))
        self.assertEqual(code, 1)
        self.assertIn("overlap", lines[0])
        self.assertIn("h1", lines[0])
        self.assertIn("svg", lines[0])
        self.assertNotIn("overflow", lines[0])

    def test_a_later_step_is_measured_too(self):
        code, lines, _ = self.check(page_with((TAKEAWAY, '<div data-step="1">' + LONG + "</div>")))
        self.assertEqual(code, 1)
        self.assertTrue(lines[2].startswith("s3  overflow"), lines[2])


if __name__ == "__main__":
    unittest.main()
