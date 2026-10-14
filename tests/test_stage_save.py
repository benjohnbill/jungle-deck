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

    def test_a_dropped_size_step_is_flagged(self):
        # #31: the student's size steps count like their words.
        saved = {"s2": '<h2 class="jd-t-l2">제목</h2><div class="panel jd-w-s1">글</div>'}
        self.assertEqual(self.flagged('<h2>제목</h2><div class="panel jd-w-s1">글</div>', saved), ["s2"])
        self.assertEqual(self.flagged('<h2 class="jd-t-l2">제목</h2><div class="panel">글</div>', saved), ["s2"])
        self.assertEqual(self.flagged('<h2 class="big jd-t-l2">제목</h2>'
                                      '<div class="jd-w-s1 panel wide">글</div>', saved), [])

    def test_ids_come_back_sorted(self):
        saved = {"s3": "<p>c</p>", "s1": "<p>a</p>"}
        self.assertEqual(run(f"overwritten({json.dumps(saved)}, "
                             f"{{s1: '<p>A</p>', s3: '<p>C</p>'}})"), ["s1", "s3"])


# A tiny element tree for the edit rule: N(tag, attrs, *children), text as str.
FAKE_DOM = """
const N = (tag, attrs, ...kids) => {
    const nodes = kids.map(k => typeof k === 'string' ? { nodeType: 3, nodeValue: k } : k);
    return { nodeType: 1, tagName: tag.toUpperCase(), name: attrs.n || tag, childNodes: nodes,
             children: nodes.filter(k => k.nodeType === 1),
             hasAttribute: a => a in attrs,
             classList: { contains: c => (attrs.class || '').split(' ').includes(c) } };
};
const names = els => els.map(e => e.name);
"""


def editable(tree):
    return run(f"(() => {{ {FAKE_DOM} return names(editableIn({tree})); }})()")


@unittest.skipUnless(NODE, "node is not installed")
class EditRuleTest(unittest.TestCase):
    """#31: every element with its own text in a slide is editable, the
    outermost one only; real run output under [data-evidence] is locked."""

    def test_outermost_element_with_its_own_text(self):
        tree = ("N('section', {}, N('div', {class: 'head'}, N('span', {n: 'topic'}, '주제'),"
                " N('span', {class: 'num', n: 'num'}, '01')),"
                " N('div', {class: 'slide-content'}, N('h2', {n: 'h2'}, '제목 ', N('em', {}, '강조')),"
                " N('ul', {}, N('li', {n: 'li'}, '항목'), N('li', {}, N('b', {n: 'b'}, '굵게')))))")
        self.assertEqual(editable(tree), ["topic", "h2", "li", "b"])

    def test_diagram_boxes_and_explanatory_code_are_editable(self):
        tree = ("N('section', {}, N('div', {class: 'box', n: 'box'}, '상자 글'),"
                " N('div', {class: 'panel'}, N('div', {class: 'cap'}, N('span', {n: 'cap'}, '코드')),"
                " N('pre', {n: 'code'}, '/* 설명 */ ', N('span', {class: 'hl'}, 'x = 1'))))")
        self.assertEqual(editable(tree), ["box", "cap", "code"])

    def test_evidence_is_locked(self):
        tree = ("N('section', {}, N('div', {class: 'panel'},"
                " N('div', {class: 'cap'}, N('span', {n: 'cap'}, 'gdb')),"
                " N('pre', {'data-evidence': '', n: 'log'}, 'Breakpoint 1', N('span', {}, 'hit'))),"
                " N('figure', {'data-evidence': ''}, N('figcaption', {n: 'fig'}, '실행 화면')))")
        self.assertEqual(editable(tree), ["cap"])

    def test_notes_svg_and_whitespace_are_skipped(self):
        tree = ("N('section', {}, N('div', {n: 'blank'}, '  \\n  ', N('p', {n: 'p'}, '글')),"
                " N('svg', {}, N('text', {n: 'svgtext'}, '라벨')),"
                " N('aside', {class: 'notes'}, N('p', {n: 'note'}, '노트')))")
        self.assertEqual(editable(tree), ["p"])


@unittest.skipUnless(NODE, "node is not installed")
class SizeStepTest(unittest.TestCase):
    """#31: size steps are classes from a fixed scale of ±2 (user said 2026-10-15)."""

    def step(self, classes, steps, d):
        return run(f"step({json.dumps(classes)}, {steps}, {d})")

    def test_text_steps_walk_the_scale_from_the_template_size(self):
        self.assertEqual(self.step(["punch"], "TEXT_STEPS", 1), ["punch", "jd-t-l1"])
        self.assertEqual(self.step(["punch", "jd-t-l1"], "TEXT_STEPS", 1), ["punch", "jd-t-l2"])
        self.assertEqual(self.step(["punch", "jd-t-l1"], "TEXT_STEPS", -1), ["punch"])
        self.assertEqual(self.step([], "TEXT_STEPS", -1), ["jd-t-s1"])

    def test_steps_stop_at_plus_and_minus_two(self):
        for steps, top, bottom in [("TEXT_STEPS", "jd-t-l2", "jd-t-s2"),
                                   ("BOX_STEPS", "jd-w-l2", "jd-w-s2")]:
            with self.subTest(steps=steps):
                self.assertEqual(self.step([top], steps, 1), [top])
                self.assertEqual(self.step([bottom], steps, -1), [bottom])
                classes = []
                for _ in range(5):
                    classes = self.step(classes, steps, 1)
                self.assertEqual(classes, [top])

    def test_zero_goes_back_to_the_template_size(self):
        self.assertEqual(self.step(["box", "jd-w-l1"], "BOX_STEPS", 0), ["box"])

    def test_the_scale_is_pinned(self):
        # Five levels each; the factors live once, as :root variables.
        self.assertEqual(run("TEXT_STEPS"), ["jd-t-s2", "jd-t-s1", None, "jd-t-l1", "jd-t-l2"])
        self.assertEqual(run("BOX_STEPS"), ["jd-w-s2", "jd-w-s1", None, "jd-w-l1", "jd-w-l2"])
        root = TEMPLATE.read_text(encoding="utf-8")
        root = root[root.index(":root {"):]
        root = root[:root.index("\n}")]
        factors = dict(re.findall(r"--(jd-[tw]-[sl]\d):\s*([\d.]+);", root))
        self.assertEqual(factors, {
            "jd-t-s2": ".75", "jd-t-s1": ".875", "jd-t-l1": "1.25", "jd-t-l2": "1.5",
            "jd-w-s2": ".75", "jd-w-s1": ".875", "jd-w-l1": "1.125", "jd-w-l2": "1.25"})


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

    def test_restore_waits_for_unsaved_edits_to_be_saved(self):
        js = self.text[self.text.index("async function restoreSaved"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("sectionHTML(document.getElementById(id)) !== base[id]", js)
        self.assertLess(js.index("if (dirty.length)"), js.index("await send("))
        self.assertIn("먼저 저장(Ctrl+S)하세요", js)

    def test_keep_drops_the_guarded_entry(self):
        js = self.text[self.text.index("async function keepAgent"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("delete saved[id]", js)
        self.assertNotIn("rememberSaved", js)

    def test_edit_mode_uses_the_edit_rule(self):
        js = self.text[self.text.index("function toggleEdit"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("slides.flatMap(s => editableIn(s))", js)
        self.assertNotIn("const EDITABLE", self.text)

    def test_size_toolbar_markup(self):
        m = re.search(r'<div id="sizeBar"[^>]*>(.*?)</div>', self.text, re.S)
        self.assertTrue(m, "no #sizeBar")
        tag = m.group(0)[:m.group(0).index(">")]
        for s in ['role="toolbar"', 'aria-label="크기 조절"', "hidden"]:
            self.assertIn(s, tag)
        for label in ["글자 작게", "글자 크게", "상자 좁게", "상자 넓게", "기본 크기"]:
            self.assertRegex(m.group(1), rf'<button[^>]*aria-label="{label}"')

    def test_every_text_step_has_a_rule_on_its_variable(self):
        css = self.text[:self.text.index("</style>")]
        for c in re.findall(r"'(jd-t-\w+)'", pure_block()):
            self.assertIn(f".{c} {{ zoom: var(--{c}); }}", css)

    def test_box_width_is_measured_clamped_and_never_saved(self):
        js = self.text[self.text.index("function fitBoxes"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("getPropertyValue('--' + s)", js)
        self.assertIn("Math.min(r.width * parseFloat(", js)
        self.assertIn("right - r.left", js)
        scrub = self.text[self.text.index("function scrub"):]
        self.assertIn("removeProperty('--box-w')", scrub[:scrub.index("\n}\n")])

    def test_toolbar_keyboard_access(self):
        js = self.text[self.text.index("document.addEventListener('keydown'"):]
        js = js[:js.index("\n});\n")]
        self.assertIn("e.key === 'Tab'", js)
        self.assertIn("sizeBar.contains(e.target)", js)
        # Tab from the toolbar goes on to the next text; Shift+Tab and Esc go back.
        self.assertIn("els[els.indexOf(selected) + 1]", js)
        self.assertIn("getSelection().addRange(caret)", js)

    def test_evidence_inside_an_editable_parent_stays_locked(self):
        js = self.text[self.text.index("function toggleEdit"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("querySelectorAll('.slide [data-evidence]').forEach(el => el.setAttribute('contenteditable', 'false'))", js)

    def test_width_steps_lift_max_width_caps(self):
        self.assertIn('.slide [style*="--box-w"] { width: var(--box-w); max-width: none; }', self.text)

    def test_size_change_autosaves_and_export_hides_the_bar(self):
        js = self.text[self.text.index("function applySize"):]
        self.assertIn("saveLocal()", js[:js.index("\n}\n")])
        exp = self.text[self.text.index("function exportFile"):]
        self.assertIn("#sizeBar", exp[:exp.index("\n}\n")])

    def test_help_names_the_size_buttons(self):
        help_box = self.text[self.text.index('<div id="helpOverlay"'):]
        help_box = help_box[:help_box.index("</dl>")]
        self.assertIn("<dt>Tab</dt>", help_box)
        self.assertIn("크기", help_box)

    def test_no_restore_by_index(self):
        self.assertNotIn("saved.data[i]", self.text)

    def test_export_drops_the_served_marks(self):
        js = self.text[self.text.index("function exportFile"):]
        js = js[:js.index("\n}\n")]
        self.assertIn("jd-base", js)
        self.assertIn("#notices", js)


if __name__ == "__main__":
    unittest.main()
