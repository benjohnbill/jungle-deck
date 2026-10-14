"""Contract checks for reference/publish.md (SPEC D12, D13, D14, D17; issues #9, #22, #26).

Run: python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLISH = ROOT / "reference" / "publish.md"
SCRIPT = ROOT / "scripts" / "publish.py"

# The publish steps, as `### N. <title>` headings, in D12 order.
STEPS = [
    "Check the save folder's repo",
    "Ask about a separate deploy",
    "Set up the Pages target",
    "Copy the page",
    "Draft the index card",
    "Ask once",
    "Commit",
    "Push",
    "Verify the live page",
    "DESIGN.md",
    "Close the BRIEF",
]


def step(text, title):
    """Return the body of the `### N. title` step, up to the next heading."""
    m = re.search(rf"^### \d+\. {re.escape(title)}[^\n]*\n(.*?)(?=^##|\Z)",
                  text, re.S | re.M)
    if not m:
        raise AssertionError(f"no '### N. {title}' step")
    return m.group(1)


def flat(text):
    """Collapse line wraps so a phrase can span two lines."""
    return re.sub(r"\s+", " ", text)


# Any text up to the end of the sentence; a file name like `x.html` does not end it.
SAME_SENTENCE = r"(?:(?!\. ).)*"


def help_text(command):
    return subprocess.run([sys.executable, str(SCRIPT), command, "--help"],
                          capture_output=True, text=True, check=True).stdout


class PublishReferenceTest(unittest.TestCase):
    def setUp(self):
        self.text = PUBLISH.read_text(encoding="utf-8")

    def rules(self):
        m = re.search(r"^## Rules\n(.*?)(?=^## )", self.text, re.S | re.M)
        self.assertTrue(m, "no '## Rules' section")
        return flat(m.group(1))

    def test_stops_the_revise_server_before_the_steps(self):
        # SPEC "Revise server": started at revise entry, stopped at publish entry.
        head = flat(self.text[:self.text.index("## Rules")])
        self.assertRegex(head, r"(?i)stop the revise server")
        self.assertIn(".serve.json", head)
        self.assertIn("/version", head)

    def test_steps_in_d12_order(self):
        found = re.findall(r"^### (\d+)\. (.+)$", self.text, re.M)
        titles = [t for _, t in found]
        positions = []
        for title in STEPS:
            hits = [i for i, t in enumerate(titles) if t.startswith(title)]
            self.assertTrue(hits, f"step '{title}' missing")
            positions.append(hits[0])
        self.assertEqual(positions, sorted(positions), "steps out of order")
        numbers = [int(n) for n, _ in found]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)), "step numbers")

    def test_no_week_repo_layout(self):
        # D5: the save folder need not be in a git repo; no weekNN/ layout.
        self.assertNotRegex(self.text, r"(?i)week repo")
        self.assertNotIn("<pages_repo>/study", self.text)

    # Step 1: repo check, safety checks before the question (D12, D13)

    def test_repo_check_asks_nothing(self):
        # #26: the commit is part of the one question in step 6.
        body = flat(step(self.text, "Check the save folder's repo"))
        self.assertRegex(body, r"git -C <save> rev-parse --show-toplevel")
        self.assertRegex(body, r"(?i)not in a git repo[^.]*skip")
        self.assertNotIn("이 저장소에 발표 자료를 커밋할까요?", self.text)

    def test_evidence_listed_and_grepped_before_commit(self):
        body = flat(step(self.text, "Check the save folder's repo"))
        self.assertRegex(body, r"(?i)list the files in `evidence/`")
        self.assertRegex(body, r"(?i)token-like strings")
        grep = re.search(r"grep -[A-Za-z]*E[A-Za-z]* '([^']+)' evidence/", body)
        self.assertTrue(grep, "no grep line for evidence/")
        pattern = re.compile(grep.group(1))
        for secret in ["ghp_" + "a" * 36, "github_pat_" + "a" * 30,
                       "sk-" + "a" * 32, "AKIA" + "A" * 16, "xoxb-123-abc",
                       "-----BEGIN RSA PRIVATE KEY-----", "api_key = abc"]:
            self.assertRegex(secret, pattern, f"pattern misses {secret!r}")
        for clean in ["PASS tests/threads/alarm-single", "Kernel panic at 0xc0000000"]:
            self.assertNotRegex(clean, pattern, f"pattern hits {clean!r}")
        self.assertRegex(body, r"(?i)before (you )?stag")
        self.assertRegex(body, r"(?i)a hit stops the commit until the student decides")

    def test_commit_set_includes_assets(self):
        body = step(self.text, "Commit")
        add = re.search(r"(?m)^\s*(git -C <save> add .*)$", body)
        self.assertTrue(add, "no git add line in the Commit step")
        for item in ["<slug>.html", "<slug>.assets/", "BRIEF.md", "evidence/", ".gitignore"]:
            self.assertIn(item, add.group(1), f"commit set lacks '{item}'")

    def test_ignore_list_in_save_folder_never_repo_root(self):
        body = flat(step(self.text, "Check the save folder's repo"))
        self.assertIn("`<save>/.gitignore`", body)
        for line in ["_backup/", "previews/", ".impeccable/", ".serve.json", ".serve.log"]:
            self.assertIn(f"`{line}`", body, f"gitignore '{line}'")
        self.assertRegex(self.rules(), r"(?i)never edit the `\.gitignore` at the repo root")

    def test_stage_named_files_never_add_all(self):
        self.assertRegex(self.text, r"(?i)stage named files only")
        self.assertRegex(self.text, r"Never use `git add -A`")
        for cmd in re.findall(r"(?m)^\s*(git (?:-C \S+ )?add .*)$", self.text):
            self.assertNotRegex(cmd, r"\s(-A|\.|--all)(\s|$)", f"bulk add: {cmd}")

    # Steps 2-3: deploy question, Pages target (D12, "Pages")

    def test_deploy_question_and_its_answers(self):
        body = flat(step(self.text, "Ask about a separate deploy"))
        self.assertIn("이 발표 페이지를 따로 배포할 생각이 있어요?", body)
        self.assertRegex(body, rf"(?i)no:{SAME_SENTENCE}print the absolute path of `<save>/<slug>\.html`")
        self.assertRegex(body, rf"(?i)another host{SAME_SENTENCE}print{SAME_SENTENCE}path{SAME_SENTENCE}stop")
        self.assertRegex(body, r"(?i)GitHub Pages is the only automated target")

    def test_pages_target_source_folder_and_gh_pages_stop(self):
        body = flat(step(self.text, "Set up the Pages target"))
        self.assertIn("지난번처럼 `<pages_repo>`에 배포할까요?", body)
        self.assertIn("gh api repos/<owner>/<repo>/pages", body)
        self.assertIn("이 저장소는 어느 폴더가 배포돼요? (루트 / docs)", body)
        self.assertRegex(body, rf"`gh-pages` branch{SAME_SENTENCE}print the absolute path{SAME_SENTENCE}stop")
        self.assertIn("`pages_dir`", body)

    def test_pages_dir_has_one_definition_in_local_template(self):
        # publish.py reads a relative pages_dir below pages_repo and an
        # absolute one as it is (tests/test_publish.py pins the code).
        local = flat((ROOT / "reference" / "local-template.md").read_text(encoding="utf-8"))
        rule = re.search(r"- `pages_dir`:(.*?)- `pages_url_base`", local)
        self.assertTrue(rule, "no pages_dir field rule in local-template.md")
        self.assertRegex(rule.group(1), r"(?i)relative value is read below `pages_repo`")
        self.assertRegex(rule.group(1), r"(?i)absolute value is used as it is")
        body = flat(step(self.text, "Set up the Pages target"))
        self.assertRegex(body, r"`reference/local-template\.md` defines the key")
        self.assertNotRegex(self.text, r"(?i)pages_dir`? (is|as) an absolute")
        self.assertNotIn("<pages_repo>/<pages_dir>", self.text)

    def test_url_confirmed_once_before_first_push(self):
        body = flat(step(self.text, "Set up the Pages target"))
        for form in ["https://<owner>.github.io/", "https://<owner>.github.io/<repo>/",
                     "https://<cname>/"]:
            self.assertIn(form, body)
        self.assertRegex(body, r"(?i)confirm[^.]*once[^.]*before the first push")
        self.assertRegex(body, r"(?i)record[^.]*`pages_url_base`")

    # Step 4: copy (publish.py copy)

    def test_copy_collision_and_replace(self):
        body = flat(step(self.text, "Copy the page"))
        self.assertIn("`--replace`", body)
        self.assertRegex(body, r"(?i)ask the student for another slug")
        self.assertIn("`--slug <new slug>`", body)
        self.assertRegex(body, r"(?i)does not delete")
        self.assertRegex(body, r"(?i)omit `--week`")
        self.assertIn("<slug>.assets/", body)

    def test_never_edit_the_pages_copy(self):
        self.assertRegex(self.text, r"(?i)never edit the pages copy")
        verify = flat(step(self.text, "Verify the live page"))
        self.assertRegex(verify, r"(?i)fix the source")
        self.assertRegex(verify, r"(?i)do not edit the pages copy")

    # Step 5: card

    def test_card_only_with_week_and_card_markup(self):
        body = flat(step(self.text, "Draft the index card"))
        self.assertRegex(body, r"(?i)week is known")
        self.assertIn('class="card"', body)
        self.assertIn("data-week", body)
        self.assertRegex(body, r"(?i)skip this step silently")

    def test_card_uses_absolute_url_from_brief(self):
        body = flat(step(self.text, "Draft the index card"))
        self.assertIn("<pages_url_base>study/weekNN/<slug>.html", body)
        self.assertRegex(body, r"(?i)full absolute URL as the `href`")
        self.assertIn("BRIEF.md", body)

    def test_any_href_that_resolves_to_the_page_url_matches(self):
        # #25: verify resolves the card href, so a relative href is no longer
        # a failure and an existing card is never rewritten.
        body = flat(step(self.text, "Draft the index card"))
        self.assertRegex(body, r"(?i)`href` that resolves to the page URL")
        for form in ["absolute", "root-relative", "relative to the index"]:
            self.assertIn(form, body)
        self.assertRegex(body, r"(?i)keep that card as it is")
        self.assertNotRegex(self.text, r"(?i)relative href fails")
        self.assertNotRegex(self.text, r"(?i)from relative to absolute")
        self.assertRegex(self.rules(), r"(?i)do not remove or rewrite an existing card\.")

    def test_pages_commit_names_assets(self):
        body = step(self.text, "Commit")
        add = re.search(r"(?m)^\s*(git -C <pages_repo> add .*)$", body)
        self.assertTrue(add, "no git add line in the Pages commit")
        self.assertIn("<slug>.html", add.group(1))
        self.assertIn("<slug>.assets/", add.group(1))

    # Steps 6-9: one question, commit, push, live check (#26)

    def test_one_question_covers_commit_and_push_of_each_repo(self):
        ask = flat(step(self.text, "Ask once"))
        self.assertIn("커밋하고 푸시할까요?", ask)
        self.assertRegex(ask, r"(?i)one question")
        self.assertRegex(ask, r"(?i)save folder's repo")
        self.assertRegex(ask, r"(?i)pages repo[^.]*when there is a deploy")
        self.assertRegex(ask, r"(?i)record the answer in `BRIEF\.md`")
        self.assertRegex(self.rules(), r"(?i)one question covers the commit and the push")

    def test_a_no_skips_git_and_still_reaches_design_md(self):
        ask = flat(step(self.text, "Ask once"))
        self.assertRegex(ask, r"(?i)not a yes, skip steps 7 to 9 and go to step 10")
        self.assertRegex(ask, r"(?i)the next publish asks again")
        self.assertNotRegex(ask, r"(?i)commit only,")

    def test_every_pass_asks_the_question_again(self):
        head = flat(self.text[:self.text.index("## Rules")])
        self.assertRegex(head, r"(?i)every pass through publish asks it again, a republish")
        self.assertRegex(head, r"(?i)holds for that pass only")

    def test_no_deploy_path_asks_the_same_question_for_the_save_repo(self):
        deploy = flat(step(self.text, "Ask about a separate deploy"))
        self.assertRegex(deploy, r"(?i)when the deploy stops[^.]*step 6[^.]*save folder's repo alone")
        ask = flat(step(self.text, "Ask once"))
        self.assertRegex(ask, r"(?i)no deploy[^.]*save folder's repo alone")
        self.assertRegex(ask, r"(?i)no repo to commit[^.]*step 10")

    def test_commit_then_push_with_no_second_question(self):
        ask = flat(step(self.text, "Ask once"))
        self.assertRegex(ask, r"(?i)commit only after an explicit yes")
        self.assertRegex(ask, r"(?i)yes or no for all the listed repos together")
        self.assertRegex(self.rules(), r"(?i)push only after an explicit yes")
        self.assertRegex(self.rules(), r"(?i)the only one about git in a pass")
        commit = flat(step(self.text, "Commit"))
        self.assertRegex(commit, r"(?i)save folder's repo.*pages repo")
        self.assertRegex(commit, r"(?i)go on to step 8 without a question")
        self.assertRegex(flat(step(self.text, "Push")), r"(?i)save folder's repo.*pages repo")
        self.assertNotRegex(self.text, r"(?i)push these repos now")

    def test_verify_checks_assets_and_card(self):
        body = flat(step(self.text, "Verify the live page"))
        self.assertRegex(body, r"(?i)each asset URL")
        self.assertRegex(body, r"(?i)only when `--week` is given")

    # Step 10: D14

    def test_design_feedback_branches_on_design_source(self):
        body = flat(step(self.text, "DESIGN.md"))
        self.assertIn("`Source`", body)
        self.assertIn("`Design` section", body)
        self.assertRegex(body, r"(?i)\bdiff\b")
        self.assertRegex(body, r"(?i)apply only the items the student picks")
        self.assertRegex(body, r"(?i)picks none, do not change DESIGN\.md")

    def test_other_source_asks_once_and_records_path(self):
        body = flat(step(self.text, "DESIGN.md"))
        other = body[body.index("Any other source"):]
        self.assertIn("이번 스타일을 DESIGN.md로 저장할까요? (새 파일 / 기존 파일 교체 / 아니요)", other)
        self.assertIn("Google Labs DESIGN.md format", other)
        self.assertRegex(other, r"`design_md` in `jungle-deck\.local\.md`")
        self.assertRegex(other, r"(?i)never merge a brand's tokens into an existing DESIGN\.md item by item")

    # Step 11

    def test_final_brief_commit_stays_local_and_student_is_told(self):
        body = flat(step(self.text, "Close the BRIEF"))
        self.assertRegex(body, r"(?i)commit stays local")
        self.assertRegex(body, r"(?i)tell the student")
        self.assertRegex(body, r"(?i)next push of the save folder's repo")
        self.assertRegex(body, r"(?i)no second (push )?confirmation")

    def test_done_is_last(self):
        body = step(self.text, "Close the BRIEF")
        self.assertIn("phase: done", body)
        self.assertRegex(body, r"(?i)only when the student confirms")

    def test_cli_lines_match_publish_py_help(self):
        lines = re.findall(r"(?m)^\s*<python_cmd> scripts/publish\.py (\w+)(.*)$", self.text)
        self.assertEqual({c for c, _ in lines}, {"copy", "verify"}, "copy and verify lines")
        for command, rest in lines:
            text = help_text(command)
            usage = text.split("\n\n")[0]
            flags = re.findall(r"--[\w-]+", rest)
            self.assertIn("--deck", flags)
            for flag in flags:
                self.assertIn(flag, text, f"{command}: unknown flag {flag}")
            # Every flag that the script requires appears in the quoted line.
            for flag in re.findall(r"(?<!\[)(--[\w-]+) [A-Z]+", usage):
                self.assertIn(flag, flags, f"{command}: required {flag} not quoted")
            # An optional flag is quoted in brackets, as in the usage line.
            for flag in re.findall(r"\[(--[\w-]+)(?: [A-Z]+)?\]", usage):
                if flag in flags:
                    self.assertRegex(rest, rf"\[{flag}\b", f"{command}: {flag} is optional")
        help_all = help_text("copy") + help_text("verify")
        for flag in re.findall(r"`(--[\w-]+)", self.text):
            self.assertIn(flag, help_all, f"prose names unknown flag {flag}")


if __name__ == "__main__":
    unittest.main()
