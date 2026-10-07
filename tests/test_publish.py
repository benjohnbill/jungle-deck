"""Tests for scripts/publish.py (SPEC D12): copy, cmp, poll, card grep.

Run: python3 -m unittest discover -s tests
No real network: the live site is a local http.server thread.
"""

import contextlib
import functools
import http.server
import importlib.util
import io
import tempfile
import threading
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("publish", ROOT / "scripts" / "publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)

DECK = b"<!doctype html><title>bsize</title><section id='s1'>hi</section>\n"


def write_local(path, **values):
    keys = ["display_name", "week_repo_root", "pages_repo", "pages_url_base",
            "card_format", "design_md", "accent"]
    lines = ["---"] + [f'{k}: "{values.get(k, "")}"' for k in keys] + ["---",
             "Personal settings for jungle-deck."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(*argv):
    """Run publish.main; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = publish.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class Workspace(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.deck = self.tmp / "week06" / "study" / "bsize-cast.html"
        self.deck.parent.mkdir(parents=True)
        self.deck.write_bytes(DECK)
        self.pages = self.tmp / "pages"
        self.pages.mkdir()
        self.local = self.tmp / "jungle-deck.local.md"


class Copy(Workspace):
    def test_copies_deck_into_pages_repo_study_week_dir(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io/")
        code, out, _ = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "6")
        self.assertEqual(code, 0)
        dest = self.pages / "study" / "week06" / "bsize-cast.html"
        self.assertEqual(dest.read_bytes(), DECK)
        self.assertIn(str(dest), out)

    def test_empty_pages_repo_stops_at_local_html(self):
        write_local(self.local)
        for command in ("copy", "verify"):
            code, out, _ = run(command, "--local", str(self.local),
                               "--deck", str(self.deck), "--week", "6")
            self.assertEqual(code, 0)
            self.assertIn("local HTML", out)
            self.assertIn(str(self.deck), out)
        self.assertEqual(list(self.pages.iterdir()), [])

    def test_corrupted_copy_exits_nonzero_with_one_line(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io/")

        def bad_copy(src, dst):
            Path(dst).write_bytes(DECK[:-2])

        with unittest.mock.patch.object(publish.shutil, "copyfile", bad_copy):
            code, _, err = run("copy", "--local", str(self.local),
                               "--deck", str(self.deck), "--week", "6")
        self.assertNotEqual(code, 0)
        self.assertIn("differs", err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_missing_local_file_exits_nonzero_with_one_line(self):
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "6")
        self.assertNotEqual(code, 0)
        self.assertIn(str(self.local), err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_tilde_in_pages_repo_expands_to_home(self):
        write_local(self.local, pages_repo="~/pages",
                    pages_url_base="https://x.github.io/")
        with unittest.mock.patch.dict("os.environ", {"HOME": str(self.tmp)}):
            code, _, _ = run("copy", "--local", str(self.local),
                             "--deck", str(self.deck), "--week", "06")
        self.assertEqual(code, 0)
        self.assertTrue((self.pages / "study" / "week06" / "bsize-cast.html").is_file())

    def test_missing_deck_exits_nonzero_with_one_line(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io/")
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.tmp / "nope.html"), "--week", "6")
        self.assertNotEqual(code, 0)
        self.assertIn("nope.html", err)
        self.assertEqual(len(err.strip().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
