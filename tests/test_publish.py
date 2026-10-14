"""Tests for scripts/publish.py (SPEC D12): copy, cmp, poll, card link.

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

DECK = b"<!doctype html><title>sample</title><section id='s1'>hi</section>\n"


def write_local(path, **values):
    keys = ["display_name", "pages_repo", "pages_dir", "pages_url_base",
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
        self.deck = self.tmp / "week03" / "study" / "sample-deck.html"
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
                           "--deck", str(self.deck), "--week", "3")
        self.assertEqual(code, 0)
        dest = self.pages / "study" / "week03" / "sample-deck.html"
        self.assertEqual(dest.read_bytes(), DECK)
        self.assertIn(str(dest), out)

    def test_no_week_copies_into_study_root(self):
        write_local(self.local, pages_repo=str(self.pages))
        code, out, err = run("copy", "--local", str(self.local), "--deck", str(self.deck))
        self.assertEqual(code, 0, err)
        self.assertEqual((self.pages / "study" / "sample-deck.html").read_bytes(), DECK)

    def test_pages_dir_receives_the_copy(self):
        (self.pages / "docs").mkdir()
        write_local(self.local, pages_repo=str(self.pages), pages_dir=str(self.pages / "docs"))
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "3")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.pages / "docs" / "study" / "week03" / "sample-deck.html").is_file())
        self.assertFalse((self.pages / "study").exists())

    def test_relative_pages_dir_is_below_pages_repo(self):
        (self.pages / "docs").mkdir()
        write_local(self.local, pages_repo=str(self.pages), pages_dir="docs")
        code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck))
        self.assertEqual(code, 0, err)
        self.assertTrue((self.pages / "docs" / "study" / "sample-deck.html").is_file())

    def test_missing_pages_dir_is_not_created(self):
        write_local(self.local, pages_repo=str(self.pages), pages_dir="docs")
        code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck))
        self.assertNotEqual(code, 0)
        self.assertIn("pages_dir", err)
        self.assertFalse((self.pages / "docs").exists())

    def test_empty_pages_repo_stops_at_local_html(self):
        write_local(self.local)
        for command in ("copy", "verify"):
            code, out, _ = run(command, "--local", str(self.local),
                               "--deck", str(self.deck), "--week", "3")
            self.assertEqual(code, 0)
            self.assertIn("local HTML", out)
            self.assertIn(str(self.deck), out)
        self.assertFalse((self.pages / "study").exists())

    def test_corrupted_copy_exits_nonzero_with_one_line(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io/")

        def bad_write(path, data):
            with open(path, "wb") as f:
                return f.write(data[:-2])

        with unittest.mock.patch.object(publish.Path, "write_bytes", bad_write):
            code, _, err = run("copy", "--local", str(self.local),
                               "--deck", str(self.deck), "--week", "3")
        self.assertNotEqual(code, 0)
        self.assertIn("differs", err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_missing_local_file_exits_nonzero_with_one_line(self):
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "3")
        self.assertNotEqual(code, 0)
        self.assertIn(str(self.local), err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_tilde_in_pages_repo_expands_to_home(self):
        write_local(self.local, pages_repo="~/pages",
                    pages_url_base="https://x.github.io/")
        with unittest.mock.patch.dict("os.environ", {"HOME": str(self.tmp)}):
            code, _, _ = run("copy", "--local", str(self.local),
                             "--deck", str(self.deck), "--week", "03")
        self.assertEqual(code, 0)
        self.assertTrue((self.pages / "study" / "week03" / "sample-deck.html").is_file())

    def test_missing_pages_repo_dir_is_not_created(self):
        typo = self.tmp / "pagse"
        write_local(self.local, pages_repo=str(typo))
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "3")
        self.assertNotEqual(code, 0)
        self.assertIn(str(typo), err)
        self.assertFalse(typo.exists())

    def test_pages_repo_without_git_gets_no_copy(self):
        plain = self.tmp / "pages-typo"
        plain.mkdir()
        write_local(self.local, pages_repo=str(plain),
                    pages_url_base="https://x.github.io/")
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "3")
        self.assertNotEqual(code, 0)
        self.assertIn("pages_repo", err)
        self.assertIn(str(plain), err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertEqual(list(plain.iterdir()), [])

    def test_missing_deck_exits_nonzero_with_one_line(self):
        write_local(self.local, pages_repo=str(self.pages),
                    pages_url_base="https://x.github.io/")
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.tmp / "nope.html"), "--week", "3")
        self.assertNotEqual(code, 0)
        self.assertIn("nope.html", err)
        self.assertEqual(len(err.strip().splitlines()), 1)


class Assets(Workspace):
    def setUp(self):
        super().setUp()
        self.assets = self.deck.parent / "sample-deck.assets"
        (self.assets / "img").mkdir(parents=True)
        (self.assets / "a.png").write_bytes(b"\x89PNG a")
        (self.assets / "img" / "b.png").write_bytes(b"\x89PNG b")
        write_local(self.local, pages_repo=str(self.pages))

    def test_assets_folder_is_copied_next_to_the_page(self):
        code, _, err = run("copy", "--local", str(self.local),
                           "--deck", str(self.deck), "--week", "3")
        self.assertEqual(code, 0, err)
        dest = self.pages / "study" / "week03" / "sample-deck.assets"
        self.assertEqual((dest / "a.png").read_bytes(), b"\x89PNG a")
        self.assertEqual((dest / "img" / "b.png").read_bytes(), b"\x89PNG b")

    def test_corrupted_asset_copy_names_the_file(self):
        def bad_write(path, data):
            with open(path, "wb") as f:
                return f.write(b"broken" if path.name == "b.png" else data)

        with unittest.mock.patch.object(publish.Path, "write_bytes", bad_write):
            code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck))
        self.assertNotEqual(code, 0)
        self.assertIn("b.png", err)
        self.assertEqual(len(err.strip().splitlines()), 1)


class Collision(Workspace):
    def setUp(self):
        super().setUp()
        write_local(self.local, pages_repo=str(self.pages))
        self.taken = self.pages / "study" / "sample-deck.html"
        self.taken.parent.mkdir(parents=True)
        self.taken.write_bytes(b"someone else's page")

    def test_existing_page_stops_copy_and_names_it(self):
        code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck))
        self.assertNotEqual(code, 0)
        self.assertIn(str(self.taken), err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertEqual(self.taken.read_bytes(), b"someone else's page")

    def test_existing_asset_stops_copy_before_any_write(self):
        self.taken.unlink()
        assets = self.deck.parent / "sample-deck.assets"
        assets.mkdir()
        (assets / "a.png").write_bytes(b"new")
        old = self.pages / "study" / "sample-deck.assets" / "a.png"
        old.parent.mkdir()
        old.write_bytes(b"old")
        code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck))
        self.assertNotEqual(code, 0)
        self.assertIn(str(old), err)
        self.assertFalse(self.taken.exists())
        self.assertEqual(old.read_bytes(), b"old")

    def test_replace_overwrites_a_republished_page(self):
        code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck),
                           "--replace")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.taken.read_bytes(), DECK)


LINKED = ('<body><section id="s1"><img src="sample-deck.assets/a.png"></section>\n'
          '<a class="home-link" href="../../">← 학습 기록</a>\n</body>').encode()


class BackLink(Workspace):
    def setUp(self):
        super().setUp()
        self.deck.write_bytes(LINKED)
        write_local(self.local, pages_repo=str(self.pages))

    def copy(self, *extra):
        code, _, err = run("copy", "--local", str(self.local), "--deck", str(self.deck), *extra)
        self.assertEqual(code, 0, err)

    def test_week_page_links_two_levels_up(self):
        (self.pages / "index.html").write_text("<h1>notes</h1>")
        self.copy("--week", "3")
        page = (self.pages / "study" / "week03" / "sample-deck.html").read_text()
        self.assertIn('<a class="home-link" href="../../">', page)

    def test_page_without_week_links_one_level_up(self):
        (self.pages / "index.html").write_text("<h1>notes</h1>")
        self.copy()
        page = (self.pages / "study" / "sample-deck.html").read_text()
        self.assertIn('<a class="home-link" href="../">← 학습 기록</a>', page)
        self.assertEqual(page.replace('href="../">', 'href="../../">').encode(), LINKED)

    def test_depth_counts_from_pages_dir(self):
        (self.pages / "docs").mkdir()
        (self.pages / "docs" / "index.html").write_text("<h1>notes</h1>")
        write_local(self.local, pages_repo=str(self.pages), pages_dir="docs")
        self.copy()
        page = (self.pages / "docs" / "study" / "sample-deck.html").read_text()
        self.assertIn('<a class="home-link" href="../">', page)

    def test_no_index_drops_the_link(self):
        self.copy("--week", "3")
        page = (self.pages / "study" / "week03" / "sample-deck.html").read_text()
        self.assertNotIn("home-link", page)
        self.assertIn('<img src="sample-deck.assets/a.png">', page)

    def test_new_slug_renames_the_asset_references(self):
        (self.deck.parent / "sample-deck.assets").mkdir()
        (self.deck.parent / "sample-deck.assets" / "a.png").write_bytes(b"png")
        self.copy("--slug", "sample-deck-2")
        page = (self.pages / "study" / "sample-deck-2.html").read_text()
        self.assertIn('<img src="sample-deck-2.assets/a.png">', page)
        self.assertTrue((self.pages / "study" / "sample-deck-2.assets" / "a.png").is_file())

    def test_source_deck_is_not_changed(self):
        self.copy()
        self.assertEqual(self.deck.read_bytes(), LINKED)


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
                       "--week", "3", "--timeout", "0", "--interval", "0")

    def test_default_from_https_origin(self):
        self.origin("https://github.com/someone/someone.github.io.git")
        write_local(self.local, pages_repo=str(self.pages))
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://someone.github.io/study/week03/sample-deck.html", err)

    def test_default_from_ssh_origin(self):
        self.origin("git@github.com:Someone/someone.github.io.git")
        write_local(self.local, pages_repo=str(self.pages))
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://someone.github.io/study/week03/sample-deck.html", err)

    def test_project_repo_origin_gives_a_project_site(self):
        self.origin("git@github.com:Someone/Talks.git")
        write_local(self.local, pages_repo=str(self.pages))
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://someone.github.io/Talks/study/week03/sample-deck.html", err)

    def test_cname_in_pages_dir_gives_the_custom_domain(self):
        self.origin("https://github.com/someone/talks.git")
        (self.pages / "docs").mkdir()
        (self.pages / "docs" / "CNAME").write_text("talks.example.org\n")
        write_local(self.local, pages_repo=str(self.pages), pages_dir="docs")
        _, _, err = self.deck_url_from_verify()
        self.assertIn("https://talks.example.org/study/week03/sample-deck.html", err)

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
        self.assertIn("https://x.github.io/study/week03/sample-deck.html", err)


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
        self.deck_url = self.base + "study/week03/sample-deck.html"
        write_local(self.local, pages_repo=str(self.pages), pages_url_base=self.base)
        (self.pages / "index.html").write_text(
            '<a class="card" data-week="2" href="https://x/old.html">old</a>')

    def go_live(self, deck=DECK, card=True, path="study/week03/sample-deck.html", index=None):
        live = self.site / path
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(deck)
        href = self.deck_url if card else "elsewhere.html"
        index = index or f'<a class="card two" href="{href}">x</a>'
        (self.site / "index.html").write_text(index)

    def verify(self, timeout="2", interval="0.05", week=("--week", "3")):
        return run("verify", "--local", str(self.local), "--deck", str(self.deck),
                   *week, "--timeout", timeout, "--interval", interval)

    def test_live_page_must_match_the_published_back_link(self):
        self.deck.write_bytes(LINKED)
        page = "study/sample-deck.html"
        self.go_live(deck=LINKED, path=page)
        code, _, err = self.verify(timeout="0.3", week=())
        self.assertNotEqual(code, 0)
        self.assertIn("differs", err)
        self.go_live(deck=LINKED.replace(b'href="../../"', b'href="../"'), path=page)
        code, _, err = self.verify(week=())
        self.assertEqual(code, 0, err)

    def test_missing_live_asset_fails_and_names_its_url(self):
        assets = self.deck.parent / "sample-deck.assets"
        assets.mkdir()
        (assets / "a.png").write_bytes(b"png")
        self.go_live()
        code, _, err = self.verify(timeout="0.3")
        self.assertNotEqual(code, 0)
        self.assertIn(self.base + "study/week03/sample-deck.assets/a.png", err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        (self.site / "study" / "week03" / "sample-deck.assets").mkdir()
        (self.site / "study" / "week03" / "sample-deck.assets" / "a.png").write_bytes(b"png")
        code, _, err = self.verify()
        self.assertEqual(code, 0, err)

    def test_no_week_checks_no_card(self):
        self.go_live(card=False, path="study/sample-deck.html")
        code, out, err = self.verify(week=())
        self.assertEqual(code, 0, err)
        self.assertIn(self.base + "study/sample-deck.html", out)

    def test_div_card_markup_also_expects_a_card(self):
        (self.pages / "index.html").write_text('<div class="wide card" data-week="2">x</div>')
        self.go_live(card=False)
        code, _, err = self.verify(timeout="0.3")
        self.assertNotEqual(code, 0)
        self.assertIn("card", err)

    def test_index_without_card_markup_checks_no_card(self):
        (self.pages / "index.html").write_text("<h1>notes</h1>")
        self.go_live(card=False)
        code, _, err = self.verify()
        self.assertEqual(code, 0, err)

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

    def test_card_href_may_be_absolute_root_relative_or_index_relative(self):
        for href in (self.deck_url, "/study/week03/sample-deck.html",
                     "study/week03/sample-deck.html", "./study/week03/sample-deck.html"):
            with self.subTest(href=href):
                self.go_live(index=f'<a class="card" href="{href}">x</a>')
                code, _, err = self.verify()
                self.assertEqual(code, 0, err)

    def test_card_href_forms_a_hand_edited_index_may_use(self):
        for anchor in ("<a class='card' href='study/week03/sample-deck.html'>",
                       '<a class="card" href = " study/week03/sample-deck.html ">',
                       '<a class="card" href="study/week03/sample%2Ddeck.html">',
                       '<a class="card" href="study/week03/sample&#45;deck.html">',
                       '<a class="card" href="study/week03/sample-deck.html#2">',
                       '<a class="card" href="study/week03/sample-deck.html?v=1">',
                       '<a href="">top</a><a class="card" href="study/week03/sample-deck.html">'):
            with self.subTest(anchor=anchor):
                self.go_live(index=anchor + "x</a>")
                code, _, err = self.verify()
                self.assertEqual(code, 0, err)

    def test_card_href_must_resolve_to_the_page_itself(self):
        for href in ("study/week03/sample-deck.html.bak", "/other/study/week03/sample-deck.html",
                     "week03/sample-deck.html", ""):
            with self.subTest(href=href):
                self.go_live(index=f'<a class="card" href="{href}">x</a>')
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
