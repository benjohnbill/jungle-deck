"""Served-mode save and autosave by section id in templates/stage.html
(SPEC "Revise server": page after a save, autosave, change notice).

The page keeps its save rules in one block of pure functions, between
`/* pure: begin */` and `/* pure: end */`. These tests run that block in
Node with sections given as {id: html}, so no browser is needed. Skipped
when `node` is not on PATH.

Run: python3 -m unittest discover -s tests
"""

import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "stage.html"
NODE = shutil.which("node")
spec = importlib.util.spec_from_file_location("serve", ROOT / "scripts" / "serve.py")
serve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(serve)


def pure_block():
    text = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"/\* pure: begin \*/(.*?)/\* pure: end \*/", text, re.S)
    if not m:
        raise AssertionError("no /* pure: begin */ ... /* pure: end */ block")
    return m.group(1)


def run(expr):
    """Evaluate a JS expression after the pure block; return its JSON value."""
    src = pure_block() + "\nprocess.stdout.write(JSON.stringify(" + expr + "));\n"
    out = subprocess.run([NODE, "-e", src], capture_output=True, text=True, timeout=30)
    if out.returncode:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout)


# The deck before and after the agent split slide s2 into s2 and a new s5.
# Slide order on the page changes; the ids s3 and s4 do not.
BEFORE = {"s1": "<h1>제목</h1>", "s2": "<p>긴 슬라이드</p>",
          "s3": "<p>원인</p>", "s4": "<p>끝</p>"}
AFTER_SPLIT = {"s1": "<h1>제목</h1>", "s2": "<p>긴 슬라이드 앞</p>",
               "s5": "<p>긴 슬라이드 뒤</p>", "s3": "<p>원인</p>",
               "s4": "<p>끝</p>"}


@unittest.skipUnless(NODE, "node is not installed")
class ChangedSectionsTest(unittest.TestCase):
    def test_only_changed_sections(self):
        cur = dict(BEFORE, s3="<p>원인 고침</p>")
        self.assertEqual(run(f"changed({json.dumps(BEFORE)}, {json.dumps(cur)})"),
                         {"s3": "<p>원인 고침</p>"})

    def test_nothing_changed(self):
        self.assertEqual(run(f"changed({json.dumps(BEFORE)}, {json.dumps(BEFORE)})"), {})


@unittest.skipUnless(NODE, "node is not installed")
class AutosaveRecordTest(unittest.TestCase):
    def test_record_holds_base_hash_base_and_current_of_changed_sections_only(self):
        cur = dict(BEFORE, s2="<p>고침</p>")
        self.assertEqual(
            run(f"autosaveRecord('h1', {json.dumps(BEFORE)}, {json.dumps(cur)})"),
            {"base_hash": "h1",
             "sections": {"s2": {"base": "<p>긴 슬라이드</p>", "current": "<p>고침</p>"}}})

    def test_no_change_means_no_record(self):
        self.assertIsNone(run(f"autosaveRecord('h1', {json.dumps(BEFORE)}, {json.dumps(BEFORE)})"))


@unittest.skipUnless(NODE, "node is not installed")
class RestoreByIdTest(unittest.TestCase):
    SAVED = {"base_hash": "old",
             "sections": {"s3": {"base": "<p>원인</p>", "current": "<p>원인 고침</p>"}}}

    def test_same_base_restores_by_id(self):
        plan = run(f"restorePlan({json.dumps(self.SAVED)}, 'old', {json.dumps(BEFORE)})")
        self.assertEqual(plan, {"stash": False, "apply": {"s3": "<p>원인 고침</p>"}})

    def test_file_changed_under_the_autosave_is_a_stash(self):
        plan = run(f"restorePlan({json.dumps(self.SAVED)}, 'new', {json.dumps(AFTER_SPLIT)})")
        self.assertEqual(plan, {"stash": True, "apply": {}})

    def test_restore_after_a_split_lands_by_id(self):
        # 복원 in file mode: a three-way merge in the page. s3 still holds its
        # base, so the edit lands on s3, now the fourth slide, not on the
        # third slide (s5).
        plan = run(f"mergeStash({json.dumps(self.SAVED)}, {json.dumps(AFTER_SPLIT)})")
        self.assertEqual(plan, {"apply": {"s3": "<p>원인 고침</p>"}, "conflicts": []})

    def test_restore_of_a_split_section_is_a_conflict(self):
        saved = {"base_hash": "old",
                 "sections": {"s2": {"base": "<p>긴 슬라이드</p>", "current": "<p>고침</p>"},
                              "s9": {"base": "<p>x</p>", "current": "<p>y</p>"}}}
        plan = run(f"mergeStash({json.dumps(saved)}, {json.dumps(AFTER_SPLIT)})")
        self.assertEqual(plan, {"apply": {}, "conflicts": ["s2", "s9"]})

    def test_served_restore_posts_the_stash_base_hash_and_its_sections(self):
        # 복원 in served mode is a normal three-way save of the stash.
        self.assertEqual(run(f"stashPayload({json.dumps(self.SAVED)})"),
                         {"base_hash": "old", "sections": {"s3": "<p>원인 고침</p>"}})

    def test_served_restore_after_a_split_lands_by_id(self):
        # The page's payload, saved by serve.py after the agent split s2.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        deck = Path(tmp.name) / "talk.html"
        deck.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
        server = serve.make_server(deck)
        self.addCleanup(server.server_close)
        _, old = server.current()
        split = deck.read_text(encoding="utf-8").replace(
            '<section class="slide" id="s3">',
            '<section class="slide" id="s5"><h2>나뉜 뒤쪽</h2></section>\n'
            '<section class="slide" id="s3">')
        deck.write_text(split, encoding="utf-8")
        stash = {"base_hash": old,
                 "sections": {"s3": {"base": "(unused by the server)",
                                     "current": "<h2>학생이 고친 원인</h2>"}}}
        status, reply = server.save(run(f"stashPayload({json.dumps(stash)})"))
        self.assertEqual((status, reply["written"]), (200, ["s3"]))
        out = deck.read_text(encoding="utf-8")
        self.assertIn('id="s5"><h2>나뉜 뒤쪽</h2></section>', out)
        self.assertIn('<section class="slide" id="s3"><h2>학생이 고친 원인</h2></section>', out)


@unittest.skipUnless(NODE, "node is not installed")
class ApplySectionsTest(unittest.TestCase):
    def test_writes_by_id_not_by_position(self):
        # Slides after a split: the third slide is now s5, s3 is fourth.
        els = "[" + ",".join(f"{{id: '{i}', innerHTML: 'old {i}'}}"
                             for i in ["s1", "s2", "s5", "s3", "s4"]) + "]"
        out = run(f"(() => {{ const els = {els}; "
                  f"applySections({{s3: 'new s3', s9: 'gone'}}, els); "
                  f"return els.map(e => e.innerHTML); }})()")
        self.assertEqual(out, ["old s1", "old s2", "old s5", "new s3", "old s4"])


@unittest.skipUnless(NODE, "node is not installed")
class OverwrittenSaveTest(unittest.TestCase):
    """#30: a student save is overwritten when the file's words differ from it.
    Words, not markup: the agent may change the layout around them."""

    SAVED = {"s2": '<div class="slide-content"><h2>학생이 쓴 <em>제목</em></h2>'
                   '<p class="punch">한 줄 결론</p></div>'}

    def flagged(self, file_s2, saved=None):
        saved = saved or self.SAVED
        return run(f"overwritten({json.dumps(saved)}, {json.dumps({'s2': file_s2})})")

    def test_changed_words_are_flagged(self):
        self.assertEqual(self.flagged('<div class="slide-content"><h2>에이전트 <em>제목</em></h2>'
                                      '<p class="punch">한 줄 결론</p></div>'), ["s2"])

    def test_a_removed_sentence_is_flagged(self):
        self.assertEqual(self.flagged('<div class="slide-content"><h2>학생이 쓴 <em>제목</em></h2></div>'),
                         ["s2"])

    def test_layout_only_change_is_not_flagged(self):
        # New wrapper, other classes, a step, indentation, the space as a <br>.
        layout = ('\n  <div class="slide-content wide"><div class="col">\n'
                  '    <h2 class="big" data-step="1">학생이 쓴<br><em>제목</em></h2>\n'
                  '    <p class="punch small">한  줄\n결론</p></div></div>\n')
        self.assertEqual(self.flagged(layout), [])

    def test_entities_compare_as_their_characters(self):
        saved = {"s2": "<p>a &lt; b &amp; c\u00a0d</p>"}
        self.assertEqual(self.flagged("<p>a &#60; b &#x26; c&nbsp;d</p>", saved), [])
        self.assertEqual(self.flagged("<p>a &lt; b &amp; c e</p>", saved), ["s2"])

    def test_a_section_gone_from_the_file_is_not_flagged(self):
        # Nothing to restore into; the server's backup still holds it.
        self.assertEqual(run(f"overwritten({json.dumps(self.SAVED)}, {{}})"), [])

    def test_ids_come_back_sorted(self):
        saved = {"s3": "<p>c</p>", "s1": "<p>a</p>"}
        self.assertEqual(run(f"overwritten({json.dumps(saved)}, "
                             f"{{s1: '<p>A</p>', s3: '<p>C</p>'}})"), ["s1", "s3"])


class ServedModeHooksTest(unittest.TestCase):
    """The browser side of the serve.py contract."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_save_request(self):
        for s in ["meta[name=\"jd-base\"]", "'/save'", "'X-Jungle-Deck': 'save'",
                  "'Content-Type': 'application/json'", "'/version'"]:
            self.assertIn(s, self.text)

    def test_poll_intervals(self):
        self.assertIn("const POLL_MS = 3000, POLL_SLOW_MS = 30000;", self.text)
        self.assertIn("misses >= 2 ? POLL_SLOW_MS : POLL_MS", self.text)

    def test_new_base_only_when_the_server_says_the_file_held_it(self):
        js = self.text[self.text.index("async function send"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("if (r.body.base_current && payload.base_hash === baseHash) baseHash = r.body.hash;", js)
        self.assertNotIn("version()", js)

    def test_old_autosave_moved_aside_is_announced(self):
        js = self.text[self.text.index("(function restoreLocal"):]
        js = js[:js.index("\n})();\n")]
        self.assertIn("':stale'", js)
        self.assertIn("notice('legacy'", js)

    def test_one_save_at_a_time(self):
        js = self.text[self.text.index("async function send"):]
        self.assertRegex(js[:js.index("\n}\n")], r"if \(saving\) return")

    def test_reload_key_is_physical(self):
        self.assertIn("e.code === 'KeyR'", self.text)

    def test_messages(self):
        for s in ["에이전트 수정과 겹쳐요", "에이전트에게 '겹친 거 합쳐줘'라고 말해 주세요",
                  "서버가 꺼져 있어요. 에이전트에게 '서버 다시 켜줘'라고 말해 주세요",
                  "자동 저장이 안 돼요 — 지금 Ctrl+S로 저장하세요",
                  "에이전트가 수정했어요 — R로 새로고침", "먼저 저장(Ctrl+S)하세요",
                  "복원", "파일로 내보내기"]:
            self.assertIn(s, self.text)

    def test_autosave_failure_is_never_silent(self):
        js = self.text[self.text.index("function saveLocal"):]
        js = js[:js.index("\n}\n")]
        self.assertNotRegex(js, r"catch \(e\) \{\s*\}")
        self.assertIn("notice('storage', STORAGE_FAILED)", js)
        self.assertIn("const STORAGE_FAILED = '자동 저장이 안 돼요", self.text)

    def test_restore_signal_is_wired(self):
        # #30: saves are remembered, checked on load and on each file change.
        t = self.text
        send = t[t.index("async function send"):]
        self.assertIn("rememberSaved(payload.sections);", send[:send.index("\n}\n")])
        self.assertIn("const SAVED = STORE + ':saved';", t)
        poll = t[t.index("async function poll"):]
        self.assertIn("checkFile()", poll[:poll.index("\n}\n")])
        self.assertIn("checkOverwrites({ ...base }, baseHash);", t)
        self.assertIn("restore: true", t)
        self.assertIn("post('/keep', { keep: ids })", t)
        for s in ["에이전트 수정 뒤 내 저장 문구가 바뀌었어요 (",
                  "에이전트에게 '복원했어'라고 말해 주세요", "'그대로 두기'"]:
            self.assertIn(s, t)

    def test_a_kept_409_payload_becomes_the_guarded_save(self):
        # The agent merges a 409 payload into the file; the guard must not
        # then offer to put the older save back over it.
        js = self.text[self.text.index("async function send"):]
        js = js[:js.index("\n}\n")]
        conflict = js[js.index("r.status === 409"):]
        self.assertIn("rememberSaved(payload.sections);", conflict[:conflict.index("} else {")])

    def test_restore_keeps_unsaved_edits_on_screen(self):
        js = self.text[self.text.index("async function restoreSaved"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("sectionHTML(document.getElementById(id)) === base[id]", js)
        self.assertNotIn("applySections(sections, slides)", js)

    def test_no_restore_by_index(self):
        self.assertNotIn("saved.data[i]", self.text)

    def test_export_drops_the_served_marks(self):
        js = self.text[self.text.index("function exportFile"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("jd-base", js)
        self.assertIn("#notices", js)


if __name__ == "__main__":
    unittest.main()
