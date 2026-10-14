---
scope: The publish phase (SPEC D12, D13, D14, D17): commit question, deploy question, Pages copy, index card, push gate, live check, DESIGN.md feedback
authority: SPEC.md D12–D14 and "Pages". CLI lines here must match `scripts/publish.py --help`; tests/test_publish_reference.py checks them
status: revised 2026-10-15 (#22); unverified draft (D19)
---

# Publish phase

The `publish` phase commits a finished presentation and, if the student
wants, puts it on their GitHub Pages site. It starts when `BRIEF.md` has
`phase: publish`. It ends when every step the student said yes to is
verified and `BRIEF.md` has `phase: done`.

Read `jungle-deck.local.md` first (keys: `reference/local-template.md`).
Record each answer and result in the `Publish` section of `BRIEF.md` when
you get it. On resume, a recorded answer is settled: do not ask it again.

## Rules

- Stage named files only. Never use `git add -A`, `git add .`, or
  `git commit -a`. The repo can hold other work, or be a shared team repo.
- The ignore list lives in `<save>/.gitignore` (D13). Never edit the
  `.gitignore` at the repo root.
- Never edit the Pages copy. Edit only the source page in the save
  folder, then copy it again with `publish.py copy`. The copy is an output.
- Push only after an explicit yes from the student (step 7). Silence, a
  question, or "잠깐" is not a yes. Without a yes, push no repo.
- Ask for the push once. Do not ask again for each repo.
- Do not change the URL of a page that is already published. Do not remove
  or rewrite an existing card. There is exactly one exception: an existing
  card for the same page URL may have its href changed from relative to
  absolute (step 5). Nothing else of an existing card changes.
- `scripts/publish.py` never runs git. You run git; the script copies and
  checks.

Placeholders: `<save>` is the absolute path of the save folder (the folder
of `BRIEF.md`). `<slug>` is `slug` and `<N>` is `week` from `BRIEF.md`.
`<page>` is the absolute path of `<save>/<slug>.html`. Run `publish.py`
from the skill directory.

## Steps

### 1. Commit in the save folder's repo

1. Run `git -C <save> rev-parse --show-toplevel`. If the save folder is
   not in a git repo, skip the rest of this step and record "not a git
   repo" in `BRIEF.md`.
2. Ask once: "이 저장소에 발표 자료를 커밋할까요?". Name the repo path.
   Record the answer in `BRIEF.md` (`Commit in this repo`). If the answer
   is no, go to `### 2. Ask about a separate deploy`.
3. Check that `<save>/.gitignore` has the lines `_backup/`, `previews/`,
   `.impeccable/`, `.serve.json`, and `.serve.log` (D13). The file is
   written when the save folder is created (`reference/brief-template.md`).
   If the file or a line is missing (an old save folder), add it there.
4. Before you stage, list the files in `evidence/` and search them for
   token-like strings. Run this in `<save>`:

   ```
   grep -rniE '(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]+|-----BEGIN [A-Z ]*PRIVATE KEY|(api[_-]?key|secret|token|passw(or)?d) *[:=])' evidence/
   ```

   Without `grep` (native Windows), use your own search tool with the same
   pattern. Show the student the file list and every hit. A hit stops the
   commit until the student decides: redact the line, leave the file out
   of the commit, or keep it as it is.
5. Stage the commit set by name. Leave out a path that does not exist
   (`<slug>.assets/` exists only when the page has images).

   ```
   git -C <save> add <slug>.html <slug>.assets/ BRIEF.md evidence/ .gitignore
   ```

6. Run `git -C <save> status --short`. Make sure that nothing else is
   staged.
7. Commit. Record the commit hash in `BRIEF.md` (`Commit in this repo`).

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

When the deploy stops: if step 1 made a commit, do steps 7 and 8 for the
save folder's repo alone, then go to step 10. Else go to step 10 directly.

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
   full absolute URL as the `href`. Do not use a relative href:
   `publish.py verify` searches the live index for the full absolute URL,
   so a relative href fails the check.
2. Fill the card format from `card_format` (`builtin`: see
   `reference/local-template.md`). Take the title, the description, and
   the meta line from `BRIEF.md`.
3. Search `<pages_dir>/index.html` for the page URL. If a card already
   links it, keep that card and do not add a second one. If the old card
   has a relative href, change only that href to the absolute URL.
4. Show the drafted card to the student. Insert it into `index.html` in the
   group of that week. If no group matches, ask the student where to put
   it.

### 6. Commit in the Pages repo

Stage the copy, its assets, and `index.html` by name. `<dir>` is the path
of `pages_dir` relative to `pages_repo`: `.` or `docs`. `[weekNN/]` is there
only with a week. Leave out `<slug>.assets/` when the page has no images,
and `index.html` when step 5 did not change it.

```
git -C <pages_repo> add <dir>/study/[weekNN/]<slug>.html <dir>/study/[weekNN/]<slug>.assets/ <dir>/index.html
```

Commit in `pages_repo`. Record the commit hash in `BRIEF.md`
(`Pages repo commit`).

### 7. Ask once

Show the student, in one message:

- each commit of this publish (`git log -1 --stat` in each repo),
- the page URL, when there is a deploy,
- the card text, when step 5 drafted one.

Ask one question: push these repos now? Push only after an explicit yes
("응", "yes", "push", "올려"). Record the answer in `BRIEF.md`
(`Push approved by student`). If the answer is not a yes, stop. Keep the
commits. Set `Next action` to "Ask the student to approve the push".

### 8. Push

Push the save folder's repo first (when step 1 made a commit), then the
Pages repo. If a push fails, show the error and stop. Do not force-push.

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
3. If step 1 made a commit, commit `BRIEF.md` alone in the save folder's
   repo. This commit stays local: do not push it, and ask no second push
   confirmation in this publish. It goes out with the next push of the
   save folder's repo.
4. Tell the student that this `phase: done` commit stays local until
   their next push of the save folder's repo.
