---
scope: The publish phase (SPEC D12, D13, D14, D17): safety checks, deploy question, Pages copy, index card, one commit-and-push question, live check, DESIGN.md feedback
authority: SPEC.md D12–D14 and "Pages". CLI lines here must match `scripts/publish.py --help`; tests/test_publish_reference.py checks them
status: revised 2026-10-15 (#22, #26); unverified draft (D19)
---

# Publish phase

The `publish` phase commits a finished presentation and, if the student
wants, puts it on their GitHub Pages site. It starts when `BRIEF.md` has
`phase: publish`. It ends when every step the student said yes to is
verified and `BRIEF.md` has `phase: done`.

Read `jungle-deck.local.md` first (keys: `reference/local-template.md`).
Record each answer and result in the `Publish` section of `BRIEF.md` when
you get it. On resume, a recorded answer is settled: do not ask it again.
The step 6 question is the exception: every pass through publish asks it
again, a republish from step 9 too. Its recorded answer holds for that
pass only.

Stop the revise server first (SPEC "Revise server"). If this session started
it, stop that background task. Else read `{port, pid}` from
`<save>/.serve.json`; when `http://127.0.0.1:<port>/version` answers with
this page as `source`, end that pid (`kill <pid>`; on Windows
`taskkill /PID <pid> /F`). No answer: the server is already off.

## Rules

- Stage named files only. Never use `git add -A`, `git add .`, or
  `git commit -a`. The repo can hold other work, or be a shared team repo.
- The ignore list lives in `<save>/.gitignore` (D13). Never edit the
  `.gitignore` at the repo root.
- Never edit the Pages copy. Edit only the source page in the save
  folder, then copy it again with `publish.py copy`. The copy is an output.
- One question covers the commit and the push of every repo in this
  publish (step 6). Commit and push only after an explicit yes from the
  student. Silence, a question, or "잠깐" is not a yes.
- That question is the only one about git in a pass. A yes runs the
  commits and the pushes in a row; a no skips them.
- Do not change the URL of a page that is already published. Do not remove
  or rewrite an existing card.
- `scripts/publish.py` never runs git. You run git; the script copies and
  checks.

Placeholders: `<save>` is the absolute path of the save folder (the folder
of `BRIEF.md`). `<slug>` is `slug` and `<N>` is `week` from `BRIEF.md`.
`<page>` is the absolute path of `<save>/<slug>.html`. Run `publish.py`
from the skill directory.

## Steps

### 1. Check the save folder's repo

This step asks nothing unless the token search hits. The commit itself
waits for the question in step 6.

1. Run `git -C <save> rev-parse --show-toplevel`. If the save folder is
   not in a git repo, skip the rest of this step and record "not a git
   repo" in `BRIEF.md` (`Commit in this repo`).
2. Check that `<save>/.gitignore` has the lines `_backup/`, `previews/`,
   `.impeccable/`, `.serve.json`, and `.serve.log` (D13). The file is
   written when the save folder is created (`reference/brief-template.md`).
   If the file or a line is missing (an old save folder), add it there.
3. Before you stage, list the files in `evidence/` and search them for
   token-like strings. Run this in `<save>`:

   ```
   grep -rniE '(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]+|-----BEGIN [A-Z ]*PRIVATE KEY|(api[_-]?key|secret|token|passw(or)?d) *[:=])' evidence/
   ```

   Without `grep` (native Windows), use your own search tool with the same
   pattern. Show the student the file list and every hit. A hit stops the
   commit until the student decides: redact the line, leave the file out
   of the commit, or keep it as it is. Record the decision; step 7 stages
   by it.

### 2. Ask about a separate deploy

Ask: "이 발표 페이지를 따로 배포할 생각이 있어요?". Record the answer in
`BRIEF.md` (`Separate deploy`). Each answer either goes on to step 3 or
stops the deploy:

- Yes, on GitHub Pages: go to step 3. GitHub Pages is the only automated
  target.
- No: print the absolute path of `<save>/<slug>.html`, then stop the
  deploy.
- Yes, on another host: print the absolute path of the page and of its
  `<slug>.assets/` folder, then stop the deploy.

When the deploy stops, go to step 6 with the save folder's repo alone.

### 3. Set up the Pages target

1. If `pages_repo` is set, ask "지난번처럼 `<pages_repo>`에 배포할까요?",
   with the path filled in. Yes: keep `pages_repo`, `pages_dir`, and
   `pages_url_base`; go to step 4. No, or `pages_repo` is empty: ask for
   the path of the local clone of the Pages repo and write it to
   `pages_repo`.
2. Find the source folder. Read `<owner>` and `<repo>` from
   `git -C <pages_repo> remote get-url origin`. With `gh` installed and
   logged in, run `gh api repos/<owner>/<repo>/pages` and read
   `source.branch` and `source.path`. Without `gh`, or when that call
   fails, ask once "이 저장소는 어느 폴더가 배포돼요? (루트 / docs)".
3. If the source is a `gh-pages` branch, print the absolute path of
   `<save>/<slug>.html` and stop the deploy (step 2). `publish.py` copies
   only into the checked-out folder, not into another branch.
4. Write `pages_dir`: `docs` for a `/docs` source, `.` for the root.
   `reference/local-template.md` defines the key and its forms.
5. Derive the page URL base, first form that applies:
   - a `CNAME` file in the `pages_dir` folder → `https://<cname>/`
   - a repo named `<owner>.github.io` → `https://<owner>.github.io/`
   - another repo → `https://<owner>.github.io/<repo>/`

   Show it and ask the student to confirm it once, before the first push.
   Then record the confirmed base in `pages_url_base`.

### 4. Copy the page

```
<python_cmd> scripts/publish.py copy --deck <page> [--week <N>] [--slug <slug>]
```

Omit `--week` when `week` in `BRIEF.md` is empty (D21). Omit `--slug` on
the first copy; a taken path below can add it. The script copies
the page and `<slug>.assets/` to `<pages_dir>/study/weekNN/` (to
`<pages_dir>/study/` without a week) and compares every file byte by byte.
The copied page differs from the source on purpose in one place: the
back-to-index link. Its `href` is fitted to the copy's depth below
`pages_dir`, or the link is removed when `pages_dir` has no `index.html`.

If the script exits non-zero, show its message and stop. Record the copy
path in `BRIEF.md` (`Pages copy path`).

When the script stops because a path is taken:

- **Taken by this presentation** (`Pages copy path` in `BRIEF.md` is the
  same path): this is a republish. Run the copy again with `--replace`.
  The URL stays the same. `--replace` does not delete asset files that
  the source no longer has: list the files in the copy's `<slug>.assets/`
  that are not in the source, and tell the student. They stay unless the
  student asks to remove them.
- **Taken by another page**: ask the student for another slug. Run the
  copy, and every later `publish.py` call, with `--slug <new slug>`. The
  script renames the `<slug>.assets/` references in the copy to match.
  Record the new slug as the published slug in `BRIEF.md`. In the steps
  below, `<slug>` is the published slug.

### 5. Draft the index card

Add a card only when the week is known and `<pages_dir>/index.html` holds
card markup of the built-in shape: a tag with `class="card"` and a
`data-week` attribute. Else skip this step silently.

1. Make the page URL: `<pages_url_base>study/weekNN/<slug>.html`. Use the
   full absolute URL as the `href`: it reaches the page from any location
   of `index.html`. `publish.py verify` accepts any `href` that resolves to
   the page URL: absolute, root-relative, or relative to the index.
2. Fill the card format from `card_format` (`builtin`: see
   `reference/local-template.md`). Take the title, the description, and
   the meta line from `BRIEF.md`.
3. Search `<pages_dir>/index.html` for a card whose `href` resolves to
   the page URL, in any of those forms. If a card already links it, keep
   that card as it is and do not add a second one.
4. Show the drafted card to the student. Insert it into `index.html` in the
   group of that week. If no group matches, ask the student where to put
   it.

### 6. Ask once

The repos in this publish: the save folder's repo (when step 1 found
one), and the Pages repo when there is a deploy. With no deploy, the
question covers the save folder's repo alone. With no repo to commit
(no git repo and no deploy), skip this question and go to step 10.

Show the student, in one message:

- each repo path, and the files that step 7 will stage in it,
- the page URL, when there is a deploy,
- the card text, when step 5 drafted one.

Ask one question: "이 저장소들에 커밋하고 푸시할까요?" (with one repo:
"이 저장소에 커밋하고 푸시할까요?"). Commit only after an explicit yes
("응", "yes", "push", "올려"). Record the answer in `BRIEF.md`
(`Push approved by student`). The answer is yes or no for all the listed
repos together. A yes goes on to step 7.

If the answer is not a yes, skip steps 7 to 9 and go to step 10. When there is a
deploy, tell the student that the Pages copy stays uncommitted in the
Pages repo. Set
`Next action` to "No commit or push in this pass; the next publish asks
again".

### 7. Commit

Commit in the save folder's repo first, then in the Pages repo.

Save folder's repo: stage the commit set by name. Leave out a path that
does not exist (`<slug>.assets/` exists only when the page has images),
and a file the student left out in step 1.

```
git -C <save> add <slug>.html <slug>.assets/ BRIEF.md evidence/ .gitignore
```

Run `git -C <save> status --short`. Make sure that nothing else is
staged. Commit. Record the commit hash in `BRIEF.md`
(`Commit in this repo`).

Pages repo: stage the copy, its assets, and `index.html` by name. `<dir>`
is the path of `pages_dir` relative to `pages_repo`: `.` or `docs`.
`[weekNN/]` is there only with a week. Leave out `<slug>.assets/` when the
page has no images, and `index.html` when step 5 did not change it.

```
git -C <pages_repo> add <dir>/study/[weekNN/]<slug>.html <dir>/study/[weekNN/]<slug>.assets/ <dir>/index.html
```

Commit in `pages_repo`. Record the commit hash in `BRIEF.md`
(`Pages repo commit`).

Then go on to step 8 without a question.

### 8. Push

Push the save folder's repo first, then the Pages repo. Push only the
repos that step 7 committed in. If a push fails, show the error and stop.
Do not force-push. Without a deploy, go to step 10 after the push.

### 9. Verify the live page

```
<python_cmd> scripts/publish.py verify --deck <page> [--week <N>] [--slug <slug>]
```

Pass the same `--week` and `--slug` as in step 4. The script polls the
page URL until it returns HTTP 200 and the live bytes match the published
copy. Then it checks each asset URL for HTTP 200. It searches the live
index for the page URL only when `--week` is given and the local
`index.html` holds built-in card markup. A Pages build takes 20–40 s,
sometimes some minutes. The default timeout is 600 s; change it with
`--timeout` only when the student asks.

- Exit 0: record the URL in `BRIEF.md` (`Live URL`, `Index card found`).
- Timeout on the page or an asset: show the reason. Run `verify` again
  later. Do not push again.
- The live page differs: fix the source page, then go back to step 1. Do
  not edit the Pages copy.
- No card: check the href in `index.html` (step 5).

### 10. DESIGN.md

D14 and D17. Do this step on every path, also when there is no deploy.
Branch on `Source` in the `Design` section of `BRIEF.md`.

If `Source` is the student's DESIGN.md:

1. Read the DESIGN.md at the path in `Source`. It is in Google Labs DESIGN.md format: YAML token
   front matter, then the sections Overview, Colors, Typography, Layout,
   Elevation & Depth, Shapes, Components, Do's and Don'ts.
2. Compare the presentation with it. List each change that this
   presentation made against DESIGN.md as one numbered diff item: the
   token or section, the old value, the new value. Example:
   `colors.accent: #d23c2c → #ff3300`.
3. Ask the student which items to apply. The student answers by number.
4. Apply only the items the student picks. Change nothing for the other
   items. If the student picks none, do not change DESIGN.md.

Any other source (a reference URL or image, a getdesign.md brand, a
`frontend-slides` pick, a vendored preset):

1. Ask once: "이번 스타일을 DESIGN.md로 저장할까요? (새 파일 / 기존 파일 교체 / 아니요)".
2. 새 파일: ask where to write it. Write the style of this presentation
   there, in Google Labs DESIGN.md format (the token front matter and the
   sections above). Record its path as `design_md` in
   `jungle-deck.local.md`. The next presentations then skip style
   discovery (D17).
3. 기존 파일 교체: write the whole file again at the path in `design_md`
   (ask for a path when it is empty), in the same format. Never merge a
   brand's tokens into an existing DESIGN.md item by item. Record the path
   as `design_md` in `jungle-deck.local.md`.
4. 아니요: change nothing.

Record the result in `BRIEF.md` (`DESIGN.md feedback`): the applied item
numbers, the written path, or "아니요". Do not commit or push DESIGN.md
unless the student asks.

### 11. Close the BRIEF

Only when the student confirms that the presentation is done (and live,
when it was deployed):

1. Set `phase: done` and `updated` in `BRIEF.md`.
2. Set `Next action` to "None. The presentation is published."
3. If step 7 made a commit in the save folder's repo, commit `BRIEF.md`
   alone there. This commit stays local: do not push it, and ask no
   second push confirmation in this publish. It goes out with the next push of the
   save folder's repo.
4. Tell the student that this `phase: done` commit stays local until
   their next push of the save folder's repo.
