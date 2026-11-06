"""Scripts print UTF-8 on a pipe, whatever the system code page is (issue #40).

Python encodes a pipe with the ANSI code page on native Windows, cp949 on Korean
Windows. PYTHONIOENCODING=cp949 gives the same stream on every OS.

Run: python3 -m unittest discover -s tests
"""

import os
import platform
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
MISSING = "없는발표"


def run_script(*argv, env=None):
    full_env = {**os.environ, "PYTHONIOENCODING": "cp949", **(env or {})}
    full_env.pop("PYTHONUTF8", None)
    return subprocess.run([sys.executable, *map(str, argv)], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=full_env, cwd=str(ROOT), timeout=120)


class ErrorsNameTheKoreanPath(unittest.TestCase):
    def assert_stderr_names_it(self, *argv):
        result = run_script(*argv)
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn(MISSING, result.stderr.decode("utf-8"))

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.deck = Path(tmp.name) / (MISSING + ".html")

    def test_check_layout(self):
        self.assert_stderr_names_it(SCRIPTS / "check_layout.py", self.deck)

    def test_serve(self):
        self.assert_stderr_names_it(SCRIPTS / "serve.py", "--deck", self.deck)

    def test_pull_edits(self):
        self.assert_stderr_names_it(SCRIPTS / "pull_edits.py", "--deck", self.deck,
                                    "--export", self.deck.with_suffix(".json"))

    def test_publish(self):
        self.assert_stderr_names_it(SCRIPTS / "publish.py", "verify", "--deck", self.deck,
                                    "--local", self.deck.with_suffix(".md"))


class StdoutNamesTheKoreanPath(unittest.TestCase):
    @unittest.skipIf("microsoft" in platform.release().lower(), "WSL asks Windows for the profile")
    def test_downloads_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "학생"
            home.mkdir()
            result = run_script(SCRIPTS / "downloads_dir.py",
                                env={"HOME": str(home), "USERPROFILE": str(home)})
        self.assertIn("학생", result.stdout.decode("utf-8"), result.stderr)


class LayoutReport(unittest.TestCase):
    def test_a_korean_overflow_is_readable_through_a_pipe(self):
        hint = '<p class="hint">덧붙일 근거나 조건 한 줄</p>'
        long = "".join("<p>넘치는 줄 %d: 글이 너무 많다</p>\n" % i for i in range(40))
        html = (ROOT / "templates" / "stage.html").read_text(encoding="utf-8")
        self.assertIn(hint, html)
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "deck.html"
            page.write_text(html.replace(hint, hint + long, 1), encoding="utf-8")
            result = run_script(SCRIPTS / "check_layout.py", page)
        if result.returncode == 3:
            self.skipTest("no headless browser")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("넘치는 줄", result.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
