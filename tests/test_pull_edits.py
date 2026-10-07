"""Tests for scripts/pull_edits.py (SPEC D11): merge a browser export back
into the deck source by <section id>.

Run: python3 -m unittest discover -s tests
Fixtures are derived from templates/stage.html in temp dirs.
"""

import contextlib
import importlib.util
import io
import os
import re
import shlex
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pull_edits", ROOT / "scripts" / "pull_edits.py")
pull_edits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pull_edits)

STAGE = (ROOT / "templates" / "stage.html").read_text(encoding="utf-8")

S1_TITLE = "발표 제목을 <em>한 줄</em>로"
S2_H2 = "<h2>이 장에서 보여 줄 <em>한 가지</em></h2>"
S1_NOTE = "무엇을 하다가 어떤 문제를 만났는지 한두 문장으로 연다."


def run(*argv):
    """Run pull_edits.main; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = pull_edits.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


def export_of(html):
    """What Ctrl+S does to sections that were not edited: the runtime fills
    each slide number, and the head and script are serialized as-is."""
    for n in range(1, 5):
        html = html.replace('<span class="num"></span>', f'<span class="num">0{n} / 04</span>', 1)
    return html


class Workspace(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.deck = self.tmp / "study" / "bsize-cast.html"
        self.deck.parent.mkdir()
        self.deck.write_text(STAGE, encoding="utf-8")
        self.downloads = self.tmp / "Downloads"
        self.downloads.mkdir()

    def export(self, html, name="bsize-cast.html", mtime=None):
        path = self.downloads / name
        path.write_text(html, encoding="utf-8")
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return path


class DryRun(Workspace):
    def test_changed_slide_text_is_shown_as_a_diff_and_not_written(self):
        exp = self.export(export_of(STAGE.replace(S1_TITLE, "힙 블록 크기는 <em>8의 배수</em>")))
        code, out, _ = run("--deck", self.deck, "--export", exp)
        self.assertEqual(code, 0)
        self.assertIn("-        <h1>발표 제목을 <em>한 줄</em>로</h1>", out)
        self.assertIn("+        <h1>힙 블록 크기는 <em>8의 배수</em></h1>", out)
        self.assertIn("s1", out)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), STAGE)

    def test_unchanged_export_reports_no_change(self):
        exp = self.export(export_of(STAGE))
        code, out, _ = run("--deck", self.deck, "--export", exp)
        self.assertEqual(code, 0)
        self.assertNotIn("@@", out)
        self.assertIn("0 changed, 4 unchanged", out)

    def test_changed_notes_are_shown_as_a_diff(self):
        exp = self.export(export_of(STAGE.replace(S1_NOTE, "malloc 이 준 크기를 먼저 의심했다.")))
        code, out, _ = run("--deck", self.deck, "--export", exp)
        self.assertEqual(code, 0)
        self.assertIn("+        <p>malloc 이 준 크기를 먼저 의심했다.</p>", out)
        self.assertIn("1 changed, 3 unchanged", out)

    def test_section_missing_in_export_is_reported_and_kept(self):
        exported = export_of(STAGE).replace('id="s3"', 'id="s3-renamed"')
        exp = self.export(exported.replace(S1_TITLE, "새 제목"))
        code, out, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        self.assertIn("missing in export: s3", out)
        self.assertIn("extra in export: s3-renamed", out)
        text = self.deck.read_text(encoding="utf-8")
        self.assertIn('<section class="slide" id="s3">\n    <div class="head"><span>정리 · 배운 것', text)
        self.assertNotIn("s3-renamed", text)
        self.assertIn("<h1>새 제목</h1>", text)

    def test_extra_slide_in_export_is_reported_not_added(self):
        extra = ('<section class="slide" id="s5">\n    <h2>새 장</h2>\n</section>\n\n'
                 '<div id="notesPanel"')
        exp = self.export(export_of(STAGE).replace('<div id="notesPanel"', extra, 1))
        code, out, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        self.assertIn("extra in export: s5", out)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), STAGE)

    def test_export_without_matching_sections_exits_non_zero(self):
        exp = self.export("<!DOCTYPE html><html><body><section class=\"slide\" id=\"x1\">a</section></body></html>")
        code, out, err = run("--deck", self.deck, "--export", exp, "--write")
        self.assertNotEqual(code, 0)
        self.assertIn("no matching sections", err)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), STAGE)

    def test_crlf_line_endings_outside_the_edit_survive(self):
        crlf = STAGE.replace("\n", "\r\n")
        self.deck.write_bytes(crlf.encode("utf-8"))
        exp = self.export(export_of(STAGE.replace(S2_H2, "<h2>새 제목</h2>")))
        code, _, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        self.assertEqual(self.deck.read_bytes(),
                         crlf.replace(S2_H2, "<h2>새 제목</h2>").encode("utf-8"))

    def test_browser_escaped_gt_is_not_a_change(self):
        src = STAGE.replace("/* 문제가 된 코드 몇 줄 */", "p->next = q;")
        self.deck.write_text(src, encoding="utf-8")
        exp = self.export(export_of(STAGE.replace("/* 문제가 된 코드 몇 줄 */", "p-&gt;next = q;")))
        code, out, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        self.assertIn("0 changed, 4 unchanged", out)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), src)


class FindExport(Workspace):
    def test_newest_browser_copy_of_this_deck_is_chosen(self):
        self.export(export_of(STAGE.replace(S1_TITLE, "오래된 사본")), "bsize-cast.html", mtime=1000)
        self.export(export_of(STAGE.replace(S1_TITLE, "가장 새 사본")), "bsize-cast (1).html", mtime=3000)
        self.export(export_of(STAGE.replace(S1_TITLE, "중간 사본")), "bsize-cast(2).html", mtime=2000)
        # Newer, but another deck: a stem prefix alone must not match it.
        self.export(export_of(STAGE.replace(S1_TITLE, "다른 덱")), "bsize-cast-v2.html", mtime=9000)
        self.export("<p>unrelated</p>", "notes.html", mtime=9500)
        code, out, _ = run("--deck", self.deck, "--downloads", self.downloads)
        self.assertEqual(code, 0)
        self.assertIn("bsize-cast (1).html", out)
        self.assertIn("+        <h1>가장 새 사본</h1>", out)

    def test_wsl_without_the_user_folder_hints_at_downloads_flag(self):
        users = self.tmp / "Users"
        (users / "someone-else" / "Downloads").mkdir(parents=True)
        self.export(export_of(STAGE.replace(S1_TITLE, "새 제목")))
        env = {"USER": "student", "HOME": str(self.tmp)}
        with unittest.mock.patch.object(pull_edits, "WIN_USERS", users), \
                unittest.mock.patch.dict(os.environ, env):
            code, out, err = run("--deck", self.deck)
        self.assertEqual(code, 0)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertIn("--downloads", err)
        self.assertIn(str(users / "student" / "Downloads"), err)
        self.assertIn(str(self.downloads), out)

    def test_wsl_user_folder_is_used_without_a_hint(self):
        users = self.tmp / "Users"
        win = users / "student" / "Downloads"
        win.mkdir(parents=True)
        (win / self.deck.name).write_text(export_of(STAGE), encoding="utf-8")
        with unittest.mock.patch.object(pull_edits, "WIN_USERS", users), \
                unittest.mock.patch.dict(os.environ, {"USER": "student"}):
            code, out, err = run("--deck", self.deck)
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn(str(win), out)

    def test_no_copy_in_downloads_exits_non_zero(self):
        self.export(export_of(STAGE), "other-deck.html")
        code, _, err = run("--deck", self.deck, "--downloads", self.downloads)
        self.assertNotEqual(code, 0)
        self.assertIn("bsize-cast", err)


class WriteNeedsExport(Workspace):
    def test_write_without_export_exits_non_zero_and_writes_nothing(self):
        self.export(export_of(STAGE.replace(S1_TITLE, "새 제목")))
        code, _, err = run("--deck", self.deck, "--downloads", self.downloads, "--write")
        self.assertNotEqual(code, 0)
        self.assertIn("--export", err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), STAGE)

    def test_dry_run_prints_the_write_command_with_the_export_it_read(self):
        exp = self.export(export_of(STAGE.replace(S1_TITLE, "새 제목")), f"{self.deck.stem} (1).html")
        code, out, _ = run("--deck", self.deck, "--downloads", self.downloads)
        self.assertEqual(code, 0)
        line = [l for l in out.splitlines() if "--write" in l]
        self.assertEqual(len(line), 1, out)
        argv = shlex.split(line[0])
        self.assertEqual(argv[0], "python3")
        self.assertEqual(argv[argv.index("--export") + 1], str(exp.resolve()))
        # Running the printed command writes exactly the reviewed export.
        code, _, _ = run(*argv[2:])
        self.assertEqual(code, 0)
        self.assertIn("<h1>새 제목</h1>", self.deck.read_text(encoding="utf-8"))


class Write(Workspace):
    def test_round_trip_changes_only_the_edited_section(self):
        # The export as Ctrl+S writes it: slide numbers filled, a typed
        # non-breaking space in the edited heading, and differences outside
        # the sections (title, style, script) that must not come back.
        exported = export_of(STAGE).replace(
            S2_H2, "<h2>bsize 는&nbsp;<em>헤더 포함</em></h2>").replace(
            "<title>발표 제목</title>", "<title>바뀐 제목</title>").replace(
            "--ink:     #111111;", "--ink:     #222222;").replace(
            "const total = slides.length;", "const total = slides.length; /* x */")
        exp = self.export(exported)
        code, out, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        self.assertIn("1 changed, 3 unchanged", out)
        expected = STAGE.replace(S2_H2, "<h2>bsize 는 <em>헤더 포함</em></h2>")
        self.assertEqual(self.deck.read_bytes(), expected.encode("utf-8"))

    def test_write_backs_up_the_deck_before_it_changes(self):
        crlf = STAGE.replace("\n", "\r\n").encode("utf-8")
        self.deck.write_bytes(crlf)
        exp = self.export(export_of(STAGE.replace(S2_H2, "<h2>새 제목</h2>")))
        code, out, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        backups = list((self.deck.parent / "_backup").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertRegex(backups[0].name, rf"^{re.escape(self.deck.stem)}\.\d{{8}}-\d{{6}}\.html$")
        self.assertEqual(backups[0].read_bytes(), crlf)
        self.assertIn(str(backups[0]), out)
        self.assertNotEqual(self.deck.read_bytes(), crlf)

    def test_failed_write_keeps_the_deck_and_leaves_no_temp_file(self):
        exp = self.export(export_of(STAGE.replace(S2_H2, "<h2>새 제목</h2>")))
        def boom(*_):
            raise OSError("disk full")
        with unittest.mock.patch.object(pull_edits.os, "replace", boom):
            code, _, err = run("--deck", self.deck, "--export", exp, "--write")
        self.assertNotEqual(code, 0)
        self.assertIn("disk full", err)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), STAGE)
        self.assertEqual(sorted(p.name for p in self.deck.parent.iterdir()),
                         ["_backup", self.deck.name])

    def test_unchanged_export_leaves_the_source_bytes_alone(self):
        exp = self.export(export_of(STAGE))
        before = self.deck.stat().st_mtime_ns
        code, _, _ = run("--deck", self.deck, "--export", exp, "--write")
        self.assertEqual(code, 0)
        self.assertEqual(self.deck.read_text(encoding="utf-8"), STAGE)
        self.assertEqual(self.deck.stat().st_mtime_ns, before)
        self.assertFalse((self.deck.parent / "_backup").exists())


if __name__ == "__main__":
    unittest.main()
