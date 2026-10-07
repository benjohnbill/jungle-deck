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
        (self.pages / ".git").mkdir(parents=True)
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
        self.assertFalse((self.pages / "study").exists())

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

    def test_missing_pages_repo_dir_is_not_created(self):
        typo = self.tmp / "pagse"
        write_local(self.local, pages_repo=str(typo))
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "6")
        self.assertNotEqual(code, 0)
        self.assertIn(str(typo), err)
        self.assertFalse(typo.exists())

    def test_pages_repo_without_git_gets_no_copy(self):
        plain = self.tmp / "pages-typo"
        plain.mkdir()
        write_local(self.local, pages_repo=str(plain),
                    pages_url_base="https://x.github.io/")
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "6")
        self.assertNotEqual(code, 0)
        self.assertIn("pages_repo", err)
        self.assertIn(str(plain), err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertEqual(list(plain.iterdir()), [])

    def test_missing_deck_exits_nonzero_with_one_line(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io/")
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.tmp / "nope.html"), "--week", "6")
        self.assertNotEqual(code, 0)
        self.assertIn("nope.html", err)
        self.assertEqual(len(err.strip().splitlines()), 1)


class Contract(unittest.TestCase):
    def test_verify_defaults_are_600_s_timeout_and_10_s_interval(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            publish.main(["verify", "--help"])
        self.assertRegex(out.getvalue(), r"--timeout[^\n]*\n?[^-]*default: 600")
        self.assertRegex(out.getvalue(), r"--interval[^\n]*\n?[^-]*default: 10\)")

    def test_script_cannot_run_git(self):
        source = (ROOT / "scripts" / "publish.py").read_text()
        for word in ("subprocess", "os.system", "popen"):
            self.assertNotIn(word, source.lower())


class UrlBase(Workspace):
    def origin(self, url):
        (self.pages / ".git" / "config").write_text(
            f'[core]\n\tbare = false\n[remote "origin"]\n\turl = {url}\n'
            '\tfetch = +refs/heads/*:refs/remotes/origin/*\n')

    def deck_url_from_verify(self):
        """verify with a fetch that never answers; the deck URL is in the message."""
        with unittest.mock.patch.object(publish, "fetch", lambda url: (None, b"")):
            return run("verify", "--local", str(self.local), "--deck", str(self.deck),
                       "--week", "6", "--timeout", "0", "--interval", "0")

    def test_default_from_https_origin(self):
        self.origin("https://github.com/someone/someone.github.io.git")
        write_local(self.local, pages_repo=str(self.pages))
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://someone.github.io/study/week06/bsize-cast.html", err)

    def test_default_from_ssh_origin(self):
        self.origin("git@github.com:Someone/someone.github.io.git")
        write_local(self.local, pages_repo=str(self.pages))
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://someone.github.io/study/week06/bsize-cast.html", err)

    def test_non_github_origin_asks_for_the_key(self):
        self.origin("https://gitlab.com/someone/site.git")
        write_local(self.local, pages_repo=str(self.pages))
        code, _, err = self.deck_url_from_verify()
        self.assertNotEqual(code, 0)
        self.assertIn("pages_url_base", err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_missing_trailing_slash_is_added(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io")
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://x.github.io/study/week06/bsize-cast.html", err)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Verify(Workspace):
    """The live site is a local http.server over self.site."""

    def setUp(self):
        super().setUp()
        self.site = self.tmp / "site"
        self.site.mkdir()
        handler = functools.partial(QuietHandler, directory=str(self.site))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.base = f"http://127.0.0.1:{server.server_address[1]}/"
        self.deck_url = self.base + "study/week06/bsize-cast.html"
        write_local(self.local, pages_repo=str(self.pages), pages_url_base=self.base)

    def go_live(self, deck=DECK, card=True):
        live = self.site / "study" / "week06" / "bsize-cast.html"
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(deck)
        href = self.deck_url if card else "elsewhere.html"
        (self.site / "index.html").write_text(f'<a class="card two" href="{href}">x</a>')

    def verify(self, timeout="2", interval="0.05"):
        return run("verify", "--local", str(self.local), "--deck", str(self.deck),
                   "--week", "6", "--timeout", timeout, "--interval", interval)

    def test_live_deck_and_card_pass_and_report_elapsed(self):
        self.go_live()
        code, out, err = self.verify()
        self.assertEqual(code, 0, err)
        self.assertIn(self.deck_url, out)
        self.assertRegex(out, r"\d+(\.\d+)? s")

    def later(self, seconds, fn):
        timer = threading.Timer(seconds, fn)
        timer.start()
        self.addCleanup(timer.cancel)

    def test_deck_that_goes_live_during_the_poll_passes(self):
        self.later(0.2, self.go_live)
        code, out, err = self.verify()
        self.assertEqual(code, 0, err)

    def test_stale_live_copy_is_polled_until_it_matches(self):
        self.go_live(deck=b"old build")
        self.later(0.2, self.go_live)
        code, out, err = self.verify()
        self.assertEqual(code, 0, err)

    def test_stale_live_copy_times_out_as_mismatch(self):
        self.go_live(deck=b"old build")
        code, _, err = self.verify(timeout="0.3")
        self.assertNotEqual(code, 0)
        self.assertIn("differs", err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_index_without_card_exits_nonzero(self):
        self.go_live(card=False)
        code, _, err = self.verify(timeout="0.3")
        self.assertNotEqual(code, 0)
        self.assertIn("card", err)
        self.assertIn(self.deck_url, err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_never_live_times_out_nonzero_with_elapsed(self):
        code, _, err = self.verify(timeout="0.3")
        self.assertNotEqual(code, 0)
        self.assertIn("404", err)
        self.assertRegex(err, r"\d+(\.\d+)? s")
        self.assertEqual(len(err.strip().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
