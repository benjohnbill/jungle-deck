"""Contract checks for reference/build.md and reference/revise.md
(SPEC D9, D10, D11, D13; issues #8, #21, #28).

Run: python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "reference" / "build.md"
REVISE = ROOT / "reference" / "revise.md"
PULL = ROOT / "scripts" / "pull_edits.py"

# Repo paths a reader of these docs is sent to. Placeholders such as
# <week repo>/study/<slug>/ are not repo paths and are not matched.
REPO_PATH = re.compile(
    r"`((?:reference|templates|scripts|vendor|tests)/[\w./-]+)`")


def section(text, heading):
    """Return the body of the `## heading` section, up to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)",
                  text, re.S | re.M)
    if not m:
        raise AssertionError(f"no '## {heading}' section")
    return m.group(1)


def flat(text):
    """Collapse line wraps so a phrase can span two lines."""
    return re.sub(r"\s+", " ", text)


class PathsExist:
    """Mixin: every repo path a doc names exists."""

    def test_named_paths_exist(self):
        paths = REPO_PATH.findall(self.text)
        self.assertTrue(paths, "doc names no repo path")
        for p in paths:
            self.assertTrue((ROOT / p).exists(), f"named path missing: {p}")


STAGE = ROOT / "templates" / "stage.html"
SERVE = ROOT / "scripts" / "serve.py"


def cli_flags(script):
    """Flags in `script --help`, and the required ones (outside [...] groups)."""
    help_text = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, check=True).stdout
    usage = help_text.split("\n\n")[0]
    # Optional groups may wrap across lines; drop them, keep the rest.
    required = re.findall(r"--[\w-]+", re.sub(r"\[[^\]]*\]", "", usage, flags=re.S))
    return help_text, required


class BuildReferenceTest(PathsExist, unittest.TestCase):
    def setUp(self):
        self.text = BUILD.read_text(encoding="utf-8")

    def test_style_only_from_design_section(self):
        # D9: the design phase (reference/design.md) owns the style source.
        body = flat(section(self.text, "Style"))
        self.assertRegex(body, r"(?i)only from the `Design` section of `BRIEF\.md`")
        self.assertIn(":root", body)
        text = flat(self.text)
        self.assertNotIn("Accent and style", text)
        self.assertNotRegex(text, r"STYLE_PRESETS|Phase 2|`design_md`")

    def test_starts_from_stage_template_at_save_folder(self):
        body = flat(section(self.text, "Start from the stage template"))
        self.assertIn("templates/stage.html", body)
        self.assertIn("<save folder>/<slug>.html", body)
        self.assertRegex(body, r"(?i)keep .*section id")
        self.assertNotRegex(flat(self.text), r"(?i)week repo")

    def test_save_folder_gitignore_only(self):
        # D13: the save folder's own .gitignore; never the repo root one.
        body = section(self.text, "Start from the stage template")
        self.assertIn("<save folder>/.gitignore", flat(body))
        for line in ["_backup/", "previews/", ".impeccable/", ".serve.json", ".serve.log"]:
            self.assertIn(f"`{line}`", body, f"gitignore '{line}'")
        self.assertRegex(flat(body), r"(?i)never edit .*repo root")

    def test_images_copied_to_assets(self):
        # D9: images go to <slug>.assets/, the original stays, no data: URIs.
        body = flat(section(self.text, "Images"))
        self.assertIn("`<slug>.assets/<file>`", body)
        self.assertRegex(body, r"(?i)copy .*from `evidence/`")
        self.assertRegex(body, r"(?i)original stays")
        self.assertRegex(body, r"(?i)never .*`data:`")
        # Only the image types serve.py serves may be named.
        served = re.search(r"IMAGE_TYPES = \{(.*?)\}", SERVE.read_text(encoding="utf-8"), re.S).group(1)
        for ext in re.findall(r"`\.(\w+)`", body):
            if ext != "svg":
                self.assertIn(f'".{ext}"', served, f"serve.py does not serve .{ext}")

    def test_theses_verbatim(self):
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)verbatim")
        self.assertRegex(body, r"(?i)do not (rephrase|reword)")
        self.assertIn("**Title slide and closing line.**", body)
        self.assertNotIn("Conclusion", body)

    def test_evidence_only_from_real_runs(self):
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)only from real runs")
        self.assertIn("evidence/", body)
        self.assertRegex(body, r"(?i)if the (log|file) is missing, (re-?run|run) the command")
        self.assertIn("source_repo", body)
        self.assertRegex(body, r"(?i)never (invent|write|type) output")

    def test_evidence_is_locked_and_boxes_resize(self):
        # #31: edit mode edits every text except real run output.
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)put `data-evidence` on each element that holds real run output")
        self.assertRegex(body, r"(?i)explanatory code and diagram boxes .*stay editable")
        self.assertIn("class `box`", body)
        self.assertRegex(body, r"(?i)`jd-t-\*` and `jd-w-\*`.*student")
        stage = STAGE.read_text(encoding="utf-8")
        self.assertIn("hasAttribute('data-evidence')", stage)
        self.assertIn("'.panel, .card, .box, .content-box, .container, [data-box]'", stage)

    def test_terms_and_notes(self):
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)define .*on (the )?screen|on-screen definition")
        self.assertRegex(body, r"(?i)light suggested script")

    def test_script_moves_into_notes(self):
        # D9: the confirmed script becomes the notes; the page is its source after build.
        body = flat(section(self.text, "Fill the slides"))
        self.assertRegex(body, r"(?i)`Script` (slot|section)")
        self.assertIn("build에서 노트로 옮김 — 이후 수정은 페이지에서", body)
        template = (ROOT / "reference" / "brief-template.md").read_text(encoding="utf-8")
        self.assertIn("build에서 노트로 옮김 — 이후 수정은 페이지에서", template)
        self.assertIn("없음 — build가 가벼운 노트를 씀", body)

    def test_no_timer_gate(self):
        text = flat(self.text)
        self.assertRegex(text, r"(?i)background, not a gate")
        self.assertRegex(text, r"(?i)no timer check")
        self.assertRegex(text, r"(?i)do not cut content only to fit")
        # No seconds budget stated as a rule.
        self.assertNotRegex(text, r"\b120\b")
        self.assertNotRegex(text, r"(?i)(must|should) (fit|stay) (in|within|under) (2|two) min")

    def test_viewport_and_density(self):
        text = flat(self.text)
        self.assertIn("vendor/frontend-slides/viewport-base.css", text)
        self.assertIn("1280×720", text)
        self.assertIn("1920×1080", text)
        self.assertRegex(text, r"(?i)density")
        self.assertRegex(text, r"(?i)never scroll")

    def test_split_uses_proposal_rule(self):
        # D7: the agent proposes the new thesis; the student picks or rewrites.
        text = flat(self.text)
        self.assertNotRegex(text, r"(?i)ask the student to write")
        self.assertRegex(text, r"(?i)split[^.]*\. [^.]*proposal rule")
        self.assertIn("reference/grill.md", text)

    def test_usage_guidance(self):
        # D9: three terminal lines that say to save and tell the agent.
        body = flat(section(self.text, "Finish"))
        self.assertRegex(body, r"(?i)three lines")
        self.assertIn("고친 뒤 저장하고 에이전트에게 말해 주세요", body)
        stage = STAGE.read_text(encoding="utf-8")
        self.assertIn("고친 뒤 저장하고 에이전트에게 말해 주세요", stage)

    def test_phase_moves_to_revise_only_on_confirmation(self):
        body = flat(section(self.text, "Finish"))
        self.assertRegex(body, r"`phase` to `revise`")
        self.assertRegex(body, r"(?i)only when the student confirms")


class ReviseReferenceTest(PathsExist, unittest.TestCase):
    def setUp(self):
        self.text = REVISE.read_text(encoding="utf-8")
        self.stage = STAGE.read_text(encoding="utf-8")

    def test_starts_or_reuses_the_server(self):
        body = flat(section(self.text, "Start the server"))
        self.assertIn("`.serve.json`", body)
        self.assertIn("/version", body)
        self.assertRegex(body, r"(?i)reuse .*only when")
        self.assertIn("`source`", body)
        self.assertIn("run_in_background", body)
        self.assertIn("http://127.0.0.1:<port>/<slug>.html", body)

    def test_serve_cli_line_matches_help(self):
        help_text, required = cli_flags(SERVE)
        lines = re.findall(r"(?m)^\s*<python_cmd> \S*scripts/serve\.py(.*)$", self.text)
        self.assertTrue(lines, "no serve.py command line")
        for rest in lines:
            flags = re.findall(r"--[\w-]+", rest)
            for flag in flags:
                self.assertIn(flag, help_text, f"unknown flag {flag}")
            for flag in required:
                self.assertIn(flag, flags, f"required {flag} not quoted")

    def test_saved_flow_reads_log_and_diff(self):
        body = flat(section(self.text, "The loop"))
        marks = ["`E`", "Ctrl+S", "저장했어, 봐줘", "`.serve.log`", "diff", "layout"]
        positions = [body.find(m) for m in marks]
        self.assertNotIn(-1, positions, f"missing a step of {marks}")
        self.assertEqual(positions, sorted(positions), "loop steps out of order")
        # #28: one round can hold several saves; the last line can hide one.
        self.assertRegex(body, r"(?i)every line of `\.serve\.log` that is newer than")

    def test_log_lines_match_serve(self):
        # The log forms the doc names are the ones serve.py writes.
        serve = SERVE.read_text(encoding="utf-8")
        for form in ['f"{verb} {', 'f"{verb} (no change)"', 'f"409 {', 'f"keep {',
                     '"restore" if restore else "save"']:
            self.assertIn(form, serve)
        body = section(self.text, "The loop")
        for form in ["save <ids> backup=", "409 <ids> payload=", "save (no change)",
                     "restore <ids> backup=", "keep <ids>"]:
            self.assertIn(form, body)

    def test_student_size_steps_are_kept(self):
        # #31: size classes the student set are treated like the student's words.
        body = flat(section(self.text, "Rules"))
        self.assertRegex(body, r"(?i)size steps .*`jd-t-\*`.*`jd-w-\*`")
        self.assertRegex(body, r"(?i)keep them in your layout pass")
        self.assertRegex(body, r"(?i)cannot fit .*proposal rule")

    def test_restore_and_keep_lines(self):
        # #30: a restore means the agent overwrote a student save.
        body = flat(section(self.text, "The loop"))
        restore = body[body.index("restore <ids> backup="):body.index("keep <ids>")]
        self.assertRegex(restore, r"(?i)re-read the page")
        self.assertIn("diff -u <backup>", restore)
        self.assertRegex(restore, r"(?i)your own change")
        self.assertRegex(restore, r"(?i)redo .*on top of the student's words.*edit rule")
        self.assertRegex(restore, r"(?i)proposal rule")
        self.assertIn("복원했어", restore)
        self.assertIn("복원했어", self.stage)
        keep = body[body.index("keep <ids>"):]
        self.assertRegex(keep[:300], r"(?i)accepted your wording")
        self.assertRegex(keep[:300], r"(?i)row \(step 7\)")

    def test_overwrite_notice_matches_template(self):
        text = flat(section(self.text, "What the student sees"))
        for s in ["에이전트 수정 뒤 내 저장 문구가 바뀌었어요 (", "그대로 두기"]:
            self.assertIn(s, text)
            self.assertIn(s, self.stage)

    def test_monitor_is_optional(self):
        text = flat(self.text)
        self.assertIn("tail -n0 -F", text)
        self.assertRegex(text, r"(?i)`Monitor`[^.]*\bmay\b|\bmay\b[^.]*`Monitor`")

    def test_conflict_handling(self):
        body = flat(section(self.text, "When the save is refused"))
        self.assertIn("겹친 거 합쳐줘", body)
        self.assertIn("_backup/rejected-", body)
        self.assertRegex(body, r"(?i)student's text")
        self.assertRegex(body, r"(?i)reload")
        self.assertIn("겹친 거 합쳐줘", self.stage)

    def test_server_off(self):
        body = flat(section(self.text, "When the save is refused"))
        self.assertIn("서버 다시 켜줘", body)
        self.assertIn("서버 다시 켜줘", self.stage)

    def test_page_behaviour_matches_template(self):
        text = flat(self.text)
        for s in ["R로 새로고침", "먼저 저장(Ctrl+S)하세요", "복원", "파일로 내보내기"]:
            self.assertIn(s, text, f"doc does not name '{s}'")
            self.assertIn(s, self.stage, f"stage.html has no '{s}'")
        poll = re.search(r"POLL_MS = (\d+), POLL_SLOW_MS = (\d+)", self.stage)
        self.assertIsNotNone(poll)
        fast, slow = (int(n) // 1000 for n in poll.groups())
        self.assertIn(f"every {fast} s", text)
        self.assertIn(f"every {slow} s", text)

    def test_keeps_student_wording(self):
        self.assertRegex(flat(self.text), r"(?i)do not (overwrite|change|rephrase) the student's wording")

    def test_new_slide_uses_proposal_rule(self):
        text = flat(self.text)
        self.assertNotRegex(text, r"(?i)ask the student (to write|for the thesis)")
        self.assertRegex(text, r"(?i)proposal rule")

    def test_records_changes_in_brief(self):
        self.assertRegex(flat(self.text), r"(?i)`Revise` (section|table) of `BRIEF\.md`")

    def test_no_week_repo(self):
        self.assertNotRegex(flat(self.text), r"(?i)week repo")

    def test_backup_folder_is_ignored(self):
        self.assertRegex(flat(self.text), r"(?i)`_backup/` is (in|listed in) the save folder['’]?s? `\.gitignore`")

    def test_agent_edits_are_targeted_on_fresh_read(self):
        # #28: a student save can land between the agent's read and write.
        body = flat(section(self.text, "Rules"))
        self.assertRegex(body, r"(?i)targeted edits? on a fresh read")
        self.assertIn("Edit tool", body)
        self.assertRegex(body, r"(?i)never rewrite the whole (file|page) from an older read")
        self.assertRegex(body, r"(?i)re-read .*every line of `\.serve\.log`.* redo")
        # The script writer the fallback uses is the named exception.
        self.assertIn("`pull_edits.py --write` is the exception", body)

    def test_agent_writers_follow_the_edit_rule(self):
        # Every place the agent writes the page points at the rule.
        loop = flat(section(self.text, "The loop"))
        refused = flat(section(self.text, "When the save is refused"))
        for name, body in [("loop", loop), ("409 merge", refused)]:
            self.assertRegex(body, r"(?i)edit rule", f"{name} does not name the edit rule")

    def test_leaves_only_when_student_says_publish(self):
        body = flat(section(self.text, "Leaving revise"))
        self.assertRegex(body, r"`phase` to `publish`")
        self.assertRegex(body, r"(?i)only when the student says to publish")
        self.assertRegex(body, r"(?i)do not (propose|suggest|ask) .*publish")


class FallbackReferenceTest(unittest.TestCase):
    """The file-export path with pull_edits.py (D11 fallback, D15)."""

    def setUp(self):
        self.text = section(REVISE.read_text(encoding="utf-8"), "Fallback: no server")

    def test_fallback_steps_in_order(self):
        body = flat(self.text)
        marks = ["Ctrl+S", "pull_edits.py", "--write", "reload"]
        positions = [body.find(m) for m in marks]
        self.assertNotIn(-1, positions, f"missing a step of {marks}")
        self.assertEqual(positions, sorted(positions), "fallback steps out of order")

    def test_dry_run_before_write_after_agreement(self):
        body = flat(self.text)
        self.assertRegex(body, r"(?i)dry-run first")
        self.assertRegex(body, r"(?i)show the student the summary")
        self.assertRegex(body, r"(?i)only after the student agrees")

    def test_script_backs_up_and_commit_comes_before_write(self):
        body = flat(self.text)
        self.assertRegex(body, r"(?i)the script copies the page to `_backup/")
        self.assertRegex(body, r"(?i)second line of defen[cs]e")
        commit, write = body.find("**Commit the page.**"), body.find("**Write.**")
        self.assertNotIn(-1, (commit, write), "no commit step or no write step")
        self.assertLess(commit, write, "commit step must come before the write step")

    def test_write_checks_for_a_newer_server_save(self):
        # #28: --write replaces sections whole; a server save after the
        # dry-run would be lost, so the dry-run runs again.
        body = flat(self.text)
        self.assertRegex(body, r"(?i)before the write, read every line of `\.serve\.log` .*newer than the dry-run")
        self.assertRegex(body, r"(?i)run the dry-run again")

    def test_reload_before_editing_again(self):
        self.assertRegex(flat(self.text), r"(?i)reload the page before (they|the student) edits? again")

    def test_cli_lines_match_pull_edits_help(self):
        help_text, required = cli_flags(PULL)
        lines = re.findall(r"(?m)^\s*<python_cmd> \S*scripts/pull_edits\.py(.*)$", self.text)
        self.assertGreaterEqual(len(lines), 2, "need a dry-run line and a --write line")
        self.assertTrue(any("--write" not in l for l in lines), "no dry-run line")
        self.assertTrue(any("--write" in l for l in lines), "no --write line")
        for rest in lines:
            flags = re.findall(r"--[\w-]+", rest)
            if "--write" in flags:
                self.assertIn("--export", flags, "--write line lacks --export")
            for flag in flags:
                self.assertIn(flag, help_text, f"unknown flag {flag}")
            for flag in required:
                self.assertIn(flag, flags, f"required {flag} not quoted")
        for span in re.findall(r"`([^`\n]+)`", self.text):
            for flag in re.findall(r"(?<![\w-])--[\w-]+", span):
                self.assertIn(flag, help_text, f"prose names unknown flag {flag}")


if __name__ == "__main__":
    unittest.main()
