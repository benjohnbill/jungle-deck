"""Tests for scripts/serve.py (SPEC D11, "Revise server"; issue #16).

Each test starts a real server on 127.0.0.1 in a thread and talks HTTP to it.
Run: python3 -m unittest discover -s tests
"""

import http.client
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("serve", ROOT / "scripts" / "serve.py")
serve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(serve)

STAGE = (ROOT / "templates" / "stage.html").read_text(encoding="utf-8")
SLUG = "sample-talk"
PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 16


class Served(unittest.TestCase):
    """A save folder with a presentation, and a running server for it."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name) / SLUG
        self.folder.mkdir()
        self.deck = self.folder / f"{SLUG}.html"
        self.deck.write_text(STAGE, encoding="utf-8")
        (self.folder / "BRIEF.md").write_text("---\nkind: jungle-deck\n---\n", encoding="utf-8")
        (self.folder / "evidence").mkdir()
        (self.folder / "evidence" / "run.txt").write_text("token=abc\n", encoding="utf-8")
        (self.folder / f"{SLUG}.assets").mkdir()
        (self.folder / f"{SLUG}.assets" / "shot.png").write_bytes(PNG)
        self.server = self.start()

    def start(self):
        server = serve.make_server(self.deck)
        t = threading.Thread(target=server.serve_forever, args=(0.05,), daemon=True)
        t.start()

        def stop():
            server.shutdown()
            server.server_close()
            t.join()
        self.addCleanup(stop)
        return server

    def request(self, method, path, body=None, headers=None, host=None, server=None):
        port = (server or self.server).port
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        h = {"Host": host or f"127.0.0.1:{port}"}
        h.update(headers or {})
        conn.request(method, path, body=body, headers=h)
        r = conn.getresponse()
        data = r.read()
        conn.close()
        return r.status, data

    def get(self, path, **kw):
        return self.request("GET", path, **kw)


class GetTest(Served):
    def test_serves_the_page_with_the_base_hash(self):
        status, body = self.get(f"/{SLUG}.html")
        self.assertEqual(status, 200)
        m = re.search(rb'<meta name="jd-base" content="([0-9a-f]+)">', body)
        self.assertTrue(m, "no jd-base meta")
        self.assertNotIn('<meta name="jd-base"', self.deck.read_text(encoding="utf-8"))
        status, v = self.get("/version")
        self.assertEqual(status, 200)
        v = json.loads(v)
        self.assertEqual(v["slug"], SLUG)
        self.assertEqual(v["source"], str(self.deck.resolve()))
        self.assertEqual(v["hash"], m.group(1).decode())

    def test_serves_asset_images(self):
        status, body = self.get(f"/{SLUG}.assets/shot.png")
        self.assertEqual((status, body), (200, PNG))

    def test_refuses_everything_else(self):
        try:   # Windows needs Developer Mode for symlinks; the rest still runs
            os.symlink(self.folder / "BRIEF.md", self.folder / f"{SLUG}.assets" / "brief.png")
        except (OSError, NotImplementedError):
            pass
        for path in ["/BRIEF.md", "/evidence/run.txt", "/_backup/x.html", "/.serve.json",
                     "/", f"/{SLUG}.assets/../BRIEF.md", f"/{SLUG}.assets/%2e%2e/BRIEF.md",
                     f"/{SLUG}.assets/brief.png", f"/{SLUG}.assets/.hidden.png"]:
            with self.subTest(path=path):
                self.assertEqual(self.get(path)[0], 404)

    def test_meta_lands_inside_a_head_with_attributes(self):
        self.deck.write_text(STAGE.replace("<head>", '<head lang="ko">'), encoding="utf-8")
        body = self.get(f"/{SLUG}.html")[1].decode("utf-8")
        self.assertTrue(body.startswith("<!DOCTYPE html>"))
        self.assertIn('<head lang="ko">\n<meta name="jd-base"', body)

    def test_symlinked_assets_folder_and_svg_are_refused(self):
        (self.folder / "x.svg").write_text("<svg/>", encoding="utf-8")
        os.replace(self.folder / f"{SLUG}.assets" / "shot.png", self.folder / "shot.png")
        shutil.rmtree(self.folder / f"{SLUG}.assets")
        try:
            os.symlink(self.folder, self.folder / f"{SLUG}.assets")
        except (OSError, NotImplementedError):
            self.skipTest("no symlinks here")
        for path in [f"/{SLUG}.assets/shot.png", f"/{SLUG}.assets/x.svg"]:
            with self.subTest(path=path):
                self.assertEqual(self.get(path)[0], 404)

    def test_options_checks_host_and_sends_no_cors(self):
        self.assertEqual(self.request("OPTIONS", "/save", host="evil.example")[0], 403)
        self.assertEqual(self.request("OPTIONS", "/save")[0], 405)

    def test_wrong_host_is_403(self):
        for host in ["evil.example", f"evil.example:{self.server.port}", "127.0.0.1:1"]:
            with self.subTest(host=host):
                self.assertEqual(self.get(f"/{SLUG}.html", host=host)[0], 403)
        self.assertEqual(self.get("/version", host=f"localhost:{self.server.port}")[0], 200)


def section_inner(html, sid):
    return next(m.group(2) for i, m in serve.pull_edits.sections(html) if i == sid)


class Saving(Served):
    def base(self):
        return json.loads(self.get("/version")[1])["hash"]

    def headers(self, **over):
        port = self.server.port
        h = {"Origin": f"http://127.0.0.1:{port}", "Content-Type": "application/json",
             "X-Jungle-Deck": "save"}
        h.update(over)
        return {k: v for k, v in h.items() if v is not None}

    def save(self, sections, base_hash=None, **over):
        body = json.dumps({"base_hash": base_hash or self.base(), "sections": sections})
        return self.request("POST", "/save", body=body.encode("utf-8"), headers=self.headers(**over))

    def agent_edit(self, sid, old, new):
        text = self.deck.read_text(encoding="utf-8")
        inner = section_inner(text, sid)
        self.assertIn(old, inner)
        self.deck.write_text(text.replace(inner, inner.replace(old, new)), encoding="utf-8")

    def edited(self, sid, old, new):
        return section_inner(self.deck.read_text(encoding="utf-8"), sid).replace(old, new)


class PostEnvelopeTest(Saving):
    def test_rejects_bad_origin_header_or_type(self):
        port = self.server.port
        cases = {
            "no origin": dict(Origin=None),
            "null origin": dict(Origin="null"),
            "foreign origin": dict(Origin="http://evil.example"),
            "other port": dict(Origin=f"http://127.0.0.1:{port + 1}"),
            "no custom header": {"X-Jungle-Deck": None},
        }
        before = self.deck.read_bytes()
        for name, over in cases.items():
            with self.subTest(name):
                self.assertEqual(self.save({"s1": "x"}, **over)[0], 403)
        self.assertEqual(self.save({"s1": "x"}, **{"Content-Type": "text/plain"})[0], 415)
        self.assertEqual(self.deck.read_bytes(), before)

    def test_rejects_non_json_and_big_bodies(self):
        status, _ = self.request("POST", "/save", body=b"not json", headers=self.headers())
        self.assertEqual(status, 400)
        # Declare an oversize body; the server must answer before reading it.
        conn = http.client.HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.putrequest("POST", "/save", skip_host=True)
        for k, v in {"Host": f"127.0.0.1:{self.server.port}", **self.headers(),
                     "Content-Length": str(5 * 1024 * 1024 + 1)}.items():
            conn.putheader(k, v)
        conn.endheaders(b"{}")
        self.assertEqual(conn.getresponse().status, 413)
        conn.close()

    def test_negative_length_is_rejected(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.putrequest("POST", "/save", skip_host=True)
        for k, v in {"Host": f"127.0.0.1:{self.server.port}", **self.headers(),
                     "Content-Length": "-1"}.items():
            conn.putheader(k, v)
        conn.endheaders()
        self.assertEqual(conn.getresponse().status, 400)
        conn.close()

    def test_wrong_host_is_403(self):
        body = json.dumps({"base_hash": self.base(), "sections": {}}).encode()
        status, _ = self.request("POST", "/save", body=body, headers=self.headers(),
                                 host="evil.example")
        self.assertEqual(status, 403)

    def test_only_one_endpoint(self):
        body = json.dumps({"base_hash": self.base(), "sections": {}}).encode()
        status, _ = self.request("POST", f"/{SLUG}.html", body=body, headers=self.headers())
        self.assertEqual(status, 404)


class ThreeWaySaveTest(Saving):
    def test_save_writes_the_changed_section(self):
        new_s2 = self.edited("s2", "한 가지", "두 가지")
        status, body = self.save({"s2": new_s2})
        self.assertEqual(status, 200)
        text = self.deck.read_text(encoding="utf-8")
        self.assertIn("두 가지", text)
        self.assertEqual(json.loads(body)["hash"], self.base())
        self.assertTrue(list((self.folder / "_backup").glob(f"{SLUG}.*.html")))

    def test_snapshot_is_seeded_at_startup(self):
        startup = serve.content_hash(self.deck.read_text(encoding="utf-8"))
        status, _ = self.save({"s2": self.edited("s2", "한 가지", "두 가지")}, base_hash=startup)
        self.assertEqual(status, 200)

    def test_agent_edit_in_s3_survives_a_stale_save_of_s2(self):
        stale = self.base()
        new_s2 = self.edited("s2", "한 가지", "두 가지")
        self.agent_edit("s3", "원인을 한 문장으로", "원인은 캐스팅 한 줄")
        status, _ = self.save({"s2": new_s2}, base_hash=stale)
        self.assertEqual(status, 200)
        text = self.deck.read_text(encoding="utf-8")
        self.assertIn("두 가지", text)
        self.assertIn("원인은 캐스팅 한 줄", text)

    def test_base_current_is_true_when_the_file_held_the_base(self):
        status, body = self.save({"s2": self.edited("s2", "한 가지", "두 가지")})
        self.assertEqual(status, 200)
        self.assertIs(json.loads(body)["base_current"], True)

    def test_base_current_is_false_after_a_write_between_snapshot_and_save(self):
        stale = self.base()
        self.agent_edit("s3", "원인을 한 문장으로", "원인은 캐스팅 한 줄")
        status, body = self.save({"s2": self.edited("s2", "한 가지", "두 가지")}, base_hash=stale)
        self.assertEqual(status, 200)
        self.assertIs(json.loads(body)["base_current"], False)

    def test_agent_edit_survives_when_the_page_keeps_its_base(self):
        # Agent edits s3; the student saves s2, then edits and saves s3. The
        # page keeps its old base when base_current is false, so the second
        # save is a 409 and the agent's s3 survives.
        page_base = self.base()
        old_s3 = section_inner(self.deck.read_text(encoding="utf-8"), "s3")
        self.agent_edit("s3", "원인을 한 문장으로", "원인은 캐스팅 한 줄")
        status, body = self.save({"s2": self.edited("s2", "한 가지", "두 가지")},
                                 base_hash=page_base)
        reply = json.loads(body)
        if reply["base_current"]:
            page_base = reply["hash"]
        status, _ = self.save({"s3": old_s3.replace("원인을 한 문장으로", "학생 원인")},
                              base_hash=page_base)
        self.assertEqual(status, 409)
        self.assertIn("원인은 캐스팅 한 줄", self.deck.read_text(encoding="utf-8"))

    def test_source_nbsp_survives_a_save_of_its_section(self):
        text = STAGE.replace("<em>한 가지</em>", "<em>64&nbsp;KB</em>")
        self.deck.write_text(text, encoding="utf-8")
        status, _ = self.save({"s2": section_inner(text, "s2").replace(
            "이 장에서", "이&nbsp;장에서 새로")})
        self.assertEqual(status, 200)
        self.assertIn("<h2>이 장에서 새로 보여 줄 <em>64&nbsp;KB</em></h2>",
                      self.deck.read_text(encoding="utf-8"))

    def test_untouched_bytes_are_never_written(self):
        crlf = STAGE.replace("\n", "\r\n")
        self.deck.write_bytes(crlf.encode("utf-8"))
        status, _ = self.save({"s2": section_inner(crlf, "s2").replace("한 가지", "두 가지")})
        self.assertEqual(status, 200)
        expected = crlf.replace("이 장에서 보여 줄 <em>한 가지</em>", "이 장에서 보여 줄 <em>두 가지</em>")
        self.assertEqual(self.deck.read_bytes(), expected.encode("utf-8"))

    def assert_rejected(self, status, body, ids, before):
        self.assertEqual(status, 409)
        reply = json.loads(body)
        self.assertEqual(sorted(reply["conflicts"]), sorted(ids))
        self.assertEqual(self.deck.read_bytes(), before)
        payload = Path(reply["payload"])
        self.assertTrue(payload.is_file())
        self.assertEqual(payload.parent.resolve(), (self.folder / "_backup").resolve())
        self.assertRegex(payload.name, r"^rejected-.*\.json$")
        return json.loads(payload.read_text(encoding="utf-8"))

    def test_conflict_writes_nothing_and_keeps_the_payload(self):
        stale = self.base()
        new_s2 = self.edited("s2", "한 가지", "두 가지")
        self.agent_edit("s2", "한 가지", "세 가지")
        before = self.deck.read_bytes()
        status, body = self.save({"s2": new_s2}, base_hash=stale)
        kept = self.assert_rejected(status, body, ["s2"], before)
        self.assertEqual(kept["sections"]["s2"], new_s2)

    def test_unknown_base_hash_is_409(self):
        before = self.deck.read_bytes()
        status, body = self.save({"s2": "x"}, base_hash="0" * 16)
        self.assert_rejected(status, body, ["s2"], before)

    def test_unknown_section_id_is_409(self):
        before = self.deck.read_bytes()
        status, body = self.save({"s2": self.edited("s2", "한 가지", "두 가지"), "s9": "x"})
        self.assert_rejected(status, body, ["s9"], before)


class ProcessTest(Saving):
    def test_port_comes_from_the_slug(self):
        self.assertEqual(serve.first_port(SLUG), 47000 + zlib.crc32(SLUG.encode()) % 1000)
        self.assertTrue(47000 <= self.server.port < 48000)

    def test_serve_json_records_port_and_pid(self):
        rec = json.loads((self.folder / ".serve.json").read_text(encoding="utf-8"))
        self.assertEqual(rec, {"port": self.server.port, "pid": os.getpid()})

    def test_a_busy_port_is_never_shared(self):
        self.assertFalse(serve.Server.allow_reuse_address)
        second = self.start()
        self.assertNotEqual(second.port, self.server.port)
        for s in (self.server, second):
            v = json.loads(self.get("/version", server=s)[1])
            self.assertEqual(v["source"], str(self.deck.resolve()))

    def test_log_has_one_line_per_save_and_per_409(self):
        stale = self.base()
        self.assertEqual(self.save({"s2": self.edited("s2", "한 가지", "두 가지")})[0], 200)
        self.assertEqual(self.save({"s2": "x"}, base_hash="0" * 16)[0], 409)
        self.assertEqual(self.save({}, base_hash=stale)[0], 200)   # nothing to write
        lines = (self.folder / ".serve.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)
        self.assertRegex(lines[2], r"^\S+ save \(no change\)$")
        self.assertRegex(lines[0], r"^\S+ save s2 backup=.*_backup")
        self.assertRegex(lines[1], r"^\S+ 409 s2 payload=.*rejected-")


class RestoreSignalTest(Saving):
    """#30: the page restores a student save that an agent edit overwrote,
    or keeps the agent's wording; the log tells the agent which."""

    def log_lines(self):
        return (self.folder / ".serve.log").read_text(encoding="utf-8").splitlines()

    def keep(self, ids, path="/keep", **over):
        body = json.dumps({"keep": ids}).encode("utf-8")
        return self.request("POST", path, body=body, headers=self.headers(**over))

    def test_restore_writes_and_logs_restore(self):
        student = self.edited("s2", "한 가지", "학생 문구")
        self.assertEqual(self.save({"s2": student})[0], 200)
        self.agent_edit("s2", "학생 문구", "에이전트 문구")
        body = json.dumps({"base_hash": self.base(), "sections": {"s2": student},
                           "restore": True}).encode("utf-8")
        status, reply = self.request("POST", "/save", body=body, headers=self.headers())
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(reply)["written"], ["s2"])
        self.assertIn("학생 문구", self.deck.read_text(encoding="utf-8"))
        self.assertNotIn("에이전트 문구", self.deck.read_text(encoding="utf-8"))
        last = self.log_lines()[-1]
        self.assertRegex(last, r"^\S+ restore s2 backup=.*_backup")
        backup = Path(last.split("backup=", 1)[1])
        self.assertIn("에이전트 문구", backup.read_text(encoding="utf-8"))

    def test_restore_that_changes_nothing_still_says_restore(self):
        body = json.dumps({"base_hash": self.base(), "sections": {},
                           "restore": True}).encode("utf-8")
        self.assertEqual(self.request("POST", "/save", body=body, headers=self.headers())[0], 200)
        self.assertRegex(self.log_lines()[-1], r"^\S+ restore \(no change\)$")

    def test_restore_must_be_a_boolean(self):
        before = self.deck.read_bytes()
        body = json.dumps({"base_hash": self.base(), "sections": {"s2": "x"},
                           "restore": "yes"}).encode("utf-8")
        self.assertEqual(self.request("POST", "/save", body=body, headers=self.headers())[0], 400)
        self.assertEqual(self.deck.read_bytes(), before)

    def test_keep_logs_the_ids_and_writes_nothing(self):
        before = self.deck.read_bytes()
        status, reply = self.keep(["s2", "s3"])
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(reply), {"kept": ["s2", "s3"]})
        self.assertEqual(self.deck.read_bytes(), before)
        self.assertRegex(self.log_lines()[-1], r"^\S+ keep s2,s3$")
        self.assertFalse((self.folder / "_backup").exists())

    def test_keep_refuses_ids_that_are_not_sections(self):
        # A forged id could plant a fake line in the log the agent reads.
        for ids in [["s9"], ["s2\n2026-01-01T00:00:00 restore s1 backup=x"], [], "s2", [2]]:
            with self.subTest(ids=ids):
                self.assertEqual(self.keep(ids)[0], 400)
        self.assertFalse((self.folder / ".serve.log").exists())

    def test_keep_has_the_save_envelope(self):
        port = self.server.port
        cases = {
            "no origin": dict(Origin=None),
            "foreign origin": dict(Origin="http://evil.example"),
            "other port": dict(Origin=f"http://127.0.0.1:{port + 1}"),
            "no custom header": {"X-Jungle-Deck": None},
        }
        for name, over in cases.items():
            with self.subTest(name):
                self.assertEqual(self.keep(["s2"], **over)[0], 403)
        self.assertEqual(self.keep(["s2"], **{"Content-Type": "text/plain"})[0], 415)
        status, _ = self.request("POST", "/keep", body=json.dumps({"keep": ["s2"]}).encode(),
                                 headers=self.headers(), host="evil.example")
        self.assertEqual(status, 403)
        status, _ = self.request("POST", "/keep", body=b"not json", headers=self.headers())
        self.assertEqual(status, 400)
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        conn.putrequest("POST", "/keep", skip_host=True)
        for k, v in {"Host": f"127.0.0.1:{port}", **self.headers(),
                     "Content-Length": str(5 * 1024 * 1024 + 1)}.items():
            conn.putheader(k, v)
        conn.endheaders(b"{}")
        self.assertEqual(conn.getresponse().status, 413)
        conn.close()
        self.assertFalse((self.folder / ".serve.log").exists())

    def test_save_refuses_ids_that_could_forge_a_log_line(self):
        before = self.deck.read_bytes()
        forged = "s2\n2026-01-01T00:00:00 keep s1"
        status, body = self.save({forged: "학생 글"})
        self.assertEqual(status, 400)
        self.assertEqual(self.deck.read_bytes(), before)
        self.assertFalse((self.folder / ".serve.log").exists())
        kept = json.loads(Path(json.loads(body)["payload"]).read_text(encoding="utf-8"))
        self.assertEqual(kept["sections"], {forged: "학생 글"})

    def test_size_steps_are_written_with_the_section(self):
        # #31: the student's size classes are part of the saved section.
        new_s2 = self.edited("s2", "<h2>", '<h2 class="jd-t-l2">').replace(
            'class="panel"', 'class="panel jd-w-s1"')
        self.assertEqual(self.save({"s2": new_s2})[0], 200)
        text = self.deck.read_text(encoding="utf-8")
        self.assertIn('<h2 class="jd-t-l2">', text)
        self.assertIn('class="panel jd-w-s1"', text)

    def test_ids_with_dots_and_digits_still_reach_the_merge(self):
        # Only whitespace and commas are refused; an unknown id is a 409 as before.
        status, _ = self.save({"2.s-a:b": "x"})
        self.assertEqual(status, 409)


if __name__ == "__main__":
    unittest.main()
