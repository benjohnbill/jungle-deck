---
scope: What the jungle-deck skill does and how it is built
authority: Design settled by grilling sessions with the user: 2026-10-07 (Q1–Q27) and 2026-10-15 (Q1–Q30, from real users' feedback), then an agent-grilling challenge of the 2026-10-15 revision (C1–C23, all items approved by the user 2026-10-15). Decisions here are the user's; change them only with the user
status: revised 2026-10-15; the revision is not implemented. main implements the 2026-10-07 design (tickets T1–T10, T13). Revision tickets: T14–T28 (GitHub Issues #14–#28)
---

# jungle-deck — spec

A Claude Code skill for Krafton Jungle students. It takes a student from
"I have something to present this week" to a 2-minute HTML presentation
(발표 자료), and optionally publishes it. It is built on the
`frontend-slides` skill and adds the Jungle context, a resumable phase
file, real evidence from the student's own runs, and a publish step.

The skill is distributed. It must not depend on the author's directory
layout, sites, or habits. The author's personal style file is not shipped.

## Users

- **The author** (benjohnbill). Uses the skill weekly, with personal
  settings in `jungle-deck.local.md`. Same code path as everyone else.
- **Other Jungle students.** Clone the public repo into
  `~/.claude/skills/jungle-deck`. They may use macOS, Windows, Linux, or
  WSL. They may not have `frontend-slides`, `grilling`, `claude-mem`, `gh`,
  any GitHub Pages site, or a `weekNN/` directory layout. Their code repo
  may be a shared team repo.

## Words

- **User-facing speech is Korean and says "발표 자료"**, never "덱" or
  "deck". Questions, messages, trigger phrases the skill offers, and the
  card badge follow this. The skill name `jungle-deck`, English documents,
  file names, and code keys (`deck:`, `data-kind="deck"`) stay as they are.
- **No Hanja in user-facing speech.** Story stages are named 도입, 전개,
  전환, 마무리.
- These two rules live in the `SKILL.md` router as the one wording rule for
  every phase.

## Decisions

| # | Decision |
|---|---|
| D1 | One skill, name `jungle-deck`. Source: `~/dev/krafton-jungle/skills/jungle-deck/`, its own git repo, public remote `benjohnbill/jungle-deck`. Installed by symlink into `~/.claude/skills/`, like `jungle-close` |
| D2 | Triggers: "발표 자료 만들자", "발표 준비", "슬라이드 만들자", "jungle-deck 이어서", "발표 자료 게시", and `/jungle-deck`. The old phrases "발표 덱" and "덱 게시" still trigger the skill, but the skill does not use them in its own speech |
| D3 | Phases: `grill → design → build → revise → publish → done`. No rehearsal phase |
| D4 | State lives in `BRIEF.md`, never only in the conversation. Its front matter holds `phase:`. On every call the skill reads BRIEF.md and resumes at that phase. A finished phase is skipped. BRIEF.md replaces handoff documents |
| D5 | Save location: when a new presentation starts, the skill asks "이번 주 발표 자료를 어디에 저장할까요?". Default: `<current directory>/<slug>/`. The save folder holds `BRIEF.md`, `<slug>.html`, `<slug>.assets/` (images), `evidence/`, and its own `.gitignore` (D13). It need not be in a git repo. No `weekNN/` layout is assumed. BRIEF front matter: `kind: jungle-deck`, `phase`, `slug`, `week` (optional, D21), `deck` (relative to the BRIEF folder), `source_repo` (D8), `created` (set once), `updated`. Resume: search `<cwd>/BRIEF.md`, then `<cwd>/*/BRIEF.md` (depth 1), then `current_brief` in local.md; a file counts only with `kind: jungle-deck` |
| D6 | Calling the skill assumes design may already be done. With no BRIEF.md, start at `grill`. With a BRIEF.md at `design` or later, skip grilling |
| D7 | `grill` settles the content, in this order. (1) Context collection (D8), no questions. (2) Context check-in (D8) and four metadata items in the same round: what to present (2–3 sharpened candidates from what the student said or from the context), why, the one line the audience should take away, and the slide count (suggest 6 ± 2; a suggestion, not a rule). Candidates in this round are marked "맥락 기준 추천"; if the check-in answer changes the sources, collect again and re-propose before recording any metadata. The takeaway line steers the grilling; it need not appear on a slide. (3) Story frame, as two questions: the structure — 오프닝 → 도입 → 전개 → 전환 → 마무리 (storytelling; recommended) or 증상 → 증거 → 원인 — and the opening — common ground (it may link to last week's topic, read from the BRIEF at `prev_brief`) or a plain topic introduction with the student's motive. A frame fixes no slide count. (4) The lead-first title slide and the closing line. (5) One thesis per slide. (6) The evidence list. (7) Terms to define on screen. (8) Script, optional: "발표 스크립트를 먼저 만들까요?" — yes: the agent drafts a full per-slide script that tells the story, with a 2-minute speaking length (about 600–700 syllables) as guidance only (D10), stored in the `Script` section of BRIEF.md; no: build writes light notes. (9) "이 내용으로 디자인을 정할까요?" before `phase` moves to `design`. **Proposal rule, everywhere** (grill, a slide split in build, a new slide in revise): the agent proposes 1–3 candidates or a draft and recommends one; the recorded text is the student's pick or rewrite |
| D8 | Context collection runs at the start of `grill`, always. `source_repo` = the git repo of the directory where the skill was called, recorded in BRIEF.md; it may differ from the save folder. Sources, in order: `git log --author=<git config user.email>` of `source_repo` and the files those commits touched, in a window since `created` of the BRIEF at `prev_brief`, else the last 7 days; the study-notes site at `notes_url`; with `gh` installed and logged in, the repo's issues, PRs, and Project board; without `gh`, a public repo's issues and PRs through the unauthenticated GitHub REST API (60 requests per hour); for a fork, the parent's issues too; `claude-mem` only when installed. The GitHub Project board needs `gh` (GraphQL requires auth). The check-in message shows what was found and what could not be read, names the `source_repo` path ("이 로컬 저장소를 기준으로 보면 될까요?"), says "본인 커밋만 봤어요" and offers the team log, and asks whether other sources exist and whether there is more the agent should know. If `notes_url` cannot be read (for example a private Notion page), ask the student to paste or export the page. Evidence commands re-run in `source_repo`; outputs go to `<save folder>/evidence/` |
| D9 | `build` uses a stage-runtime template (derived from the author's own stage-runtime deck, content removed): fixed slides, one active, `#N` hash, per-element `data-step`, speaker notes on `N`, in-browser edit mode on `E`, save on `Ctrl+S`. Build reads the style only from the `Design` section of BRIEF.md. Speaker notes are the confirmed script (D7 item 8) or a light suggested script; after build, the page notes are the script's source of truth, and BRIEF `Script` gets the line "build에서 노트로 옮김 — 이후 수정은 페이지에서". Images are copied from `evidence/` into `<slug>.assets/` (the original stays) and referenced as `<slug>.assets/<file>`; never `data:` URIs. Usage guidance: at the end of build, three lines in the terminal (how to open, the keys, what to do after an edit); in the page, a `?` key shortcut overlay and a one-time hint on first open. Both say "고친 뒤 저장하고 에이전트에게 말해 주세요". Template text: no "질문 받을게요"; the notes panel labels time as "참고 시간" and "참고 합계" |
| D10 | The 2-minute limit is background, not a gate. No timer check. Do not cut content only to fit a timer. Slide-count and script-length numbers are suggestions |
| D11 | `revise` is the main loop. The agent starts `scripts/serve.py` and the student opens the presentation through it. Save in the page writes straight into the source file by a three-way merge per section (see "Revise server" below). Default flow: the student saves, then tells the agent ("저장했어, 봐줘"); the agent reads the last line of `.serve.log` and the diff, and adjusts layout and evidence. Where the Claude Code `Monitor` tool works, the agent may also run `tail -n0 -F .serve.log` and react on its own. No in-page request notes. Fallback without the server (page opened as a file): `Ctrl+S` exports to the downloads folder and `scripts/pull_edits.py` merges it (two-way, with the "reload before editing again" rule) |
| D12 | `publish`, in this order (#26). First, if the save folder is in a git repo, list the `evidence/` files and grep them for token-like strings; a hit stops the commit until the student decides. Then ask "이 발표 페이지를 따로 배포할 생각이 있어요?". No: no Pages step; print the local HTML path. Yes: GitHub Pages is the only automated target (see "Pages" below). Another host: print the HTML path and stop. Copy the HTML and `<slug>.assets/` to `<pages_dir>/study/weekNN/` when the week is known, else `<pages_dir>/study/`, and `cmp` every file. `copy` and `verify` compare against the published page (home-link `href` fitted to its depth), not the source bytes. A path collision stops `publish.py copy`, which names the file. `publish.py copy --replace` republishes over the same path, only when BRIEF "Pages copy path" equals it; old asset files stay and are listed to the student. A path taken by another page: the agent asks for another slug. Add the index card only when the week is known and `index.html` holds card markup of the built-in shape (`class="card"` with `data-week`); else skip it silently. Keep the back-to-index link only when `index.html` exists; its `href` is computed from the real depth below `pages_dir`. After the copy and the card, ask ONE question for commit and push that covers the save repo and, when deploying, the Pages repo (no deploy: the save repo alone; no repo at all: skip). The answer is yes or no for all of them, holds for this pass only, and is recorded in BRIEF.md. Yes: commit the presentation, `<slug>.assets/`, BRIEF.md, and `evidence/` by name (save repo, then Pages repo), then push with no second question. No: nothing is committed; the Pages copy stays uncommitted and the student is told. Poll until the URL returns 200, `cmp` the live page, check each live asset URL for 200, and check the index for the card when `--week` is given and the local `index.html` has card markup (#25). Edit only the source, never the copy. Existing published pages keep their URLs |
| D13 | Ignore list in `<save folder>/.gitignore`: `_backup/`, `previews/`, `.impeccable/`, `.serve.json`, `.serve.log`. Never edit the repo root `.gitignore` |
| D14 | Design feedback at `publish` branches on `source` in the `Design` section of BRIEF.md. Source is the student's DESIGN.md: show what this presentation changed against it as a diff; apply only the items the student picks. Any other source: ask once "이번 스타일을 DESIGN.md로 저장할까요? (새 파일 / 기존 파일 교체 / 아니요)" (Google Labs DESIGN.md format), and record the path in local.md. Never merge a brand's tokens into an existing DESIGN.md item by item |
| D15 | Dependencies: use it if present, else a built-in fallback. `grilling` → inline round rules. `frontend-slides` → vendored files with the MIT notice. `claude-mem` → skip. `gh` → public REST API for public repos; skip the Project board; ask for the Pages source folder. `Monitor` → the student tells the agent after each save. Server not running → file export and `pull_edits.py`. No publish target → stop after a finished local HTML |
| D16 | Personal settings: `jungle-deck.local.md` in the skill directory, gitignored. Fields: `display_name`, `notes_url`, `design_md`, `accent`, `downloads_dir`, `python_cmd`, `current_brief` (set when a presentation is created; resume), `prev_brief` (the old `current_brief` moves here on create; last week's topic and the D8 window), `pages_repo`, `pages_dir`, `pages_url_base` (written at publish), `card_format`. First run asks only display name and study-notes site; both may be `""`. `design_md` and the accent are asked in `design`; `downloads_dir` the first time the fallback runs. Migration: an existing file keeps working; `week_repo_root` and `last_brief` are ignored; a key that is missing (not empty) is asked once when it is first needed; an empty value `""` is a valid answer and is never asked again |
| D17 | `design` phase, between `grill` and `build`. (1) With `design_md` set: "이번에도 이 스타일로 갈까요?" — yes: confirm the accent, then done. (2) Else, or no: ask "원하는 디자인 레퍼런스가 있어요? (사이트 URL, 이미지, DESIGN.md)" and "getdesign.md 레퍼런스 중에서 고를까요?". (3) Style source, first that applies: the student's reference > a getdesign.md pick (D25) > `frontend-slides` style discovery > vendored presets. (4) Two or three previews, the student picks, then the accent. (5) Record `source`, tokens, and accent in the `Design` section of BRIEF.md. Move to `build` only on the student's confirmation. A dark-canvas reference: warn about the bright room, allow it |
| D18 | Template page: one fixed page pinned at the top of `benjohnbill.github.io`, no week or topic. It holds the phase diagram, the one-line install, the first-run questions, the author's three presentations as examples, and links to `frontend-slides` and the skill repo. Built only after the skill works and the publish path is verified |
| D19 | Verification state is written into the skill. After this revision, every phase is an unverified draft. `revise` and `publish` are first verified on a nearly finished presentation; `grill`, `design`, and `build` on the next new one. The manual checks under "Verification plan" are recorded in the phase files as they pass |
| D20 | Portability (2026-10-07): the skill runs on macOS, Windows, Linux, and WSL. The downloads folder default is detected per OS, and the student confirms it into `downloads_dir`; on WSL with no answer, ask, do not guess. Python 3.8 or later: the first run tries `python3`, `python`, `py -3` and records the first that works as `python_cmd`. Check again only when it is empty or fails. Never install Python |
| D21 | The week number is optional. Read it silently from a `week\d+` part of the save path into BRIEF.md `week:`; never ask for it. With no week: the title slide drops its week line, `publish.py --week` is omitted, the Pages path has no week folder, and no index card is added |
| D22 | Shared context is general (see the next section). It must hold for C weeks, Pintos weeks, and the later Python and AI weeks. Evidence is real output the student ran — test results or terminal logs — never invented, and not tied to a named toolchain |
| D23 | An existing BRIEF.md in the old format is recognized by `phase:` + `slug:` + `deck:` in its front matter. Migration adds `kind: jungle-deck`, and `created` from the date of the first commit that touched the BRIEF, else `updated`. At `phase: grill`, add each new slot (metadata, story frame questions, title slide, script, design) as `TBD` and keep the filled slots; the old `Conclusion` slot maps to the title slide. At `build` or later, change nothing else |
| D24 | No author-specific values ship. The reference files use generic examples (`display_name: 홍길동`, `pages_repo: ~/my-pages`, `downloads_dir: ~/Downloads`). A contract test over `git ls-files`, excluding `SPEC.md`, `LICENSE`, and the README clone-URL line, fails on `benjohnbill`, `/mnt/c/Users/`, `krafton-jungle/`, and `week_repo_root` |
| D25 | getdesign.md references (VoltAgent `awesome-design-md`, MIT, Google DESIGN.md format): list the brands from the repo through raw GitHub URLs; no `npx`. Recommend 2–3 by mood and link each preview at `getdesign.md/<brand>/design-md`. A brand that is not in the repo: the student downloads it from the site and gives the path. A file with no front matter is not recommended; if the student picks it, treat it as the student's own reference. Mapping into `stage.html` `:root`, first key present wins: `--paper` ← `canvas`; `--ink` ← `ink`; `--acc` ← `primary`; `--mut` ← `ink-mute`, `ink-muted`, `muted`, `mute`, `ink-subtle`, `body`; `--panel` ← `canvas-soft`, `surface-soft`, `surface-1`, `surface`; `--grid` ← `hairline`, `hairline-soft`; an empty chain for `--paper` or `--ink` → keep the template value; for `--mut`, `--panel`, or `--grid` → the `color-mix()` of ink and paper. If `primary` equals `ink` or has contrast below 3:1 against `--paper` (the background), take the first saturated color (`link`, `brand-*`) that passes the same 3:1 test against `--paper`, and ask the student to confirm the accent; the fallback uses the same test (#27). Font family only, with a Korean font appended and a note when a paid font falls back to a system font; keep the template's `clamp()` sizes and take only weight, letter spacing, and line height; drop components and decorative signatures. When the agent proposes a reference, it says first that only the color and type mood transfer, and points to `frontend-slides` presets for a full slide style. Measured coverage (2026-10-15, 84 files): no front matter 10/84; of 74 with front matter, `canvas-soft` 19, `ink-mute` 5, `primary == ink` 24, dark canvas 14 |
| D26 | README holds the whole workflow as tables: per phase, what the skill asks and what the student decides. The tables are a reader summary; SPEC wins on conflict. It also has a troubleshooting table (WSL `localhostForwarding=false`, server off, Monitor unavailable) |

## Revise server (D11)

- **Process.** `scripts/serve.py`, stdlib only, Python 3.8+. Bind
  `127.0.0.1`. `allow_reuse_address = False`; on Windows set
  `SO_EXCLUSIVEADDRUSE` before bind, so a busy port fails on every OS.
  Port `47000 + crc32(slug) % 1000`, next free port on a clash. Record
  `{port, pid}` in `<save folder>/.serve.json`. Revise entry reuses the
  recorded server only when `GET /version` names this presentation's source;
  else it starts a new one and rewrites `.serve.json`. Started by the agent
  at the end of build (`run_in_background`; the "how to open" line needs
  the saving address), reused at revise entry by that identity check,
  stopped at publish entry. One URL
  only: `http://127.0.0.1:<port>/<slug>.html`.
- **Security envelope.** Every request: `Host` must be `127.0.0.1:<port>` or
  `localhost:<port>`, else 403 (DNS rebinding). POST: one fixed endpoint; the
  write target is the source file fixed at startup, and the client never
  sends a path. POST needs the custom header and an `Origin` of exactly
  `http://127.0.0.1:<port>` or `http://localhost:<port>`; a missing or
  `null` Origin is rejected. `Content-Type: application/json`; body cap
  5 MB. GET serves only the presentation file, `/version`, and image files
  under `<slug>.assets/`; it refuses dotfiles, `_backup/`, `BRIEF.md`, and
  `evidence/`, and resolves symlinks before the containment check. Writes
  reuse `pull_edits.backup` and `write_atomic`.
- **Three-way save.** The server keeps a snapshot of each served version by
  hash, seeded with the current file at startup, and injects
  `<meta name="jd-base" content="<hash>">` into the served page (not on
  disk). The page captures `base` per section id at load, before any
  autosave restore. On Ctrl+S it sends `base_hash` and only the sections
  where `current != base`. The server writes those sections only if each
  source section still equals the snapshot at `base_hash` (backup, atomic).
  Any failure, an unknown `base_hash`, or a sent id that is not in the
  source → 409 with the ids; nothing is written; the payload goes to
  `_backup/rejected-<stamp>.json`. Sections the student did not touch are
  never written.
- **Page after a save.** 2xx: clear the autosave; adopt the returned hash
  as `base_hash` and the current sections as `base` only when the response
  says `base_current: true` (decided under the save lock); else keep the
  old base. 409: edit mode off;
  banner "에이전트 수정과 겹쳐요 (<ids>). 에이전트에게 '겹친 거 합쳐줘'라고 말해
  주세요"; when the response confirms the payload file, clear the
  autosave. The agent applies the student's text from the payload into the
  current source (the student owns the words), then asks for a reload.
  Network failure: fall back to the download export, with "서버가 꺼져
  있어요. 에이전트에게 '서버 다시 켜줘'라고 말해 주세요".
- **Autosave.** Stored by section id: `{base_hash, base, current}` for
  changed sections only. A stash (the file changed under the autosave)
  shows a notice with "복원" (= a normal three-way save of the stash) and
  "파일로 내보내기". In file mode, 복원 is a three-way merge in the page;
  slides that also changed in the file stay out, with an export notice.
  Every notice has "닫기" (hides it for this load). Never a DOM write by index. A `localStorage` failure
  shows "자동 저장이 안 돼요 — 지금 Ctrl+S로 저장하세요"; never a silent catch.
- **Change notice.** `GET /version` → `{slug, source, hash}`. The page
  polls every 3 s while served. Hash ≠ `base_hash`: no unsaved edits →
  "에이전트가 수정했어요 — R로 새로고침"; unsaved edits → "먼저
  저장(Ctrl+S)하세요". `R` is matched by `e.code === 'KeyR'` (works with a
  Korean IME) and keeps `#N`. After two failed polls: stop, show the
  server-off message, retry every 30 s.
- **Agent writes.** Targeted edits on a fresh read of the source only, so
  a student save between reads survives (#28).
- **Log.** One line per save or 409 in `<save folder>/.serve.log`: time,
  section ids, backup or payload path.

## Pages (D12)

- URL: a repo named `<owner>.github.io` → `https://<owner>.github.io/`;
  another repo → `https://<owner>.github.io/<repo>/`; a `CNAME` file →
  `https://<cname>/`.
- Source folder: with `gh`, `gh api repos/<owner>/<repo>/pages`
  (`source.branch`, `source.path`); without it, ask once "이 저장소는 어느
  폴더가 배포돼요? (루트 / docs)" and record `pages_dir`. A `gh-pages` branch
  source: print the HTML path and stop.
- Show the derived URL and confirm it once before the first push; record
  `pages_url_base`. With `pages_repo` already set, ask "지난번처럼
  `<path>`에 배포할까요?".

## Shared Jungle context (ships in the skill)

From the user's own words (sessions 2026-09-16 to 2026-10-15): a weekly
Thursday talk; the topic is what the student learned this week —
troubleshooting or an experiment story is recommended, in a refined,
WIL-like form; the title slide is lead-first; audience = the cohort on
the same week's curriculum, wide level spread, more than half know the
topic; Korean; 2 minutes, no Q&A; large monitor in a bright lecture room;
storytelling is preferred ("2분이지만 발표는 스토리텔링"); the
presentation also feeds the student's WIL. Speaker, publishing, and style
rows are personal and live in local.md.

## Template tokens

`templates/stage.html` derives `--hl`, `--edit-bg`, `--cap-b`, `--shadow`,
`--dim`, `--scrim`, and `--panel-b` from `--acc`, `--ink`, and `--paper` with `color-mix()`. A
style source then sets only `--paper`, `--ink`, `--acc`, `--mut`,
`--panel`, `--grid`, and the fonts. This also fixes the DESIGN.md path,
where those five tokens stayed slate.

## Repository layout (target)

```
jungle-deck/
├─ SKILL.md                 # router: triggers, find BRIEF, dispatch phase, dependency checks
├─ README.md                # install, first run, workflow tables, troubleshooting (D26), credits
├─ LICENSE
├─ SPEC.md                  # this file
├─ reference/
│  ├─ context.md            # shared Jungle context (D22)
│  ├─ brief-template.md     # BRIEF.md skeleton + phase contract + migration (D23)
│  ├─ grill.md              # D7, D8, inline grilling rules
│  ├─ design.md             # D17, D25
│  ├─ build.md              # D9, D10
│  ├─ revise.md             # D11
│  ├─ publish.md            # D12–D14, card format, Pages
│  └─ local-template.md     # D16 fields, first-run questions, migration
├─ templates/stage.html     # D9, template tokens, served-mode page logic
├─ scripts/
│  ├─ pull_edits.py         # D11 fallback merge by section id
│  ├─ serve.py              # D11 revise server
│  ├─ downloads_dir.py      # D20 downloads folder per OS
│  └─ publish.py            # D12 copy, cmp, poll, assets, card link check (no push)
├─ tests/                   # unittest; contract tests for the reference files
├─ vendor/frontend-slides/  # viewport-base.css etc. + MIT LICENSE
└─ .gitignore               # jungle-deck.local.md
```

## Verification plan

Automated (unittest, before any real use):

- serve.py: `Host` 403; missing, `null`, or foreign Origin rejected; no
  custom header rejected; non-JSON and over 5 MB rejected; GET refuses
  `BRIEF.md`, `evidence/`, `_backup/`, dotfiles, and a symlink escape; GET
  serves `<slug>.assets/*.png`.
- Three-way save: the agent edits s3, a stale page saves s2, s3 survives; a
  conflict gives 409, writes nothing, and writes `_backup/rejected-*.json`;
  an unknown `base_hash` gives 409; the snapshot is seeded at startup.
- Two servers for one slug on Linux: the second gets another port;
  `/version` identity check.
- Autosave by id: 복원 after a slide split lands by id (JS unit test of the
  restore function, or a headless browser).
- publish.py: the three URL forms; back-link depth with and without a
  week; assets copied and compared; collision stop; `--replace`; copy and
  verify against the fitted page; the verify card check (#25).
- getdesign mapping over the 84 files: every file with front matter yields
  all mapped tokens or a derived value, and an accent different from `ink`.
- The D24 grep test; contract tests for the reference files updated (the
  old "student writes the thesis" and "week repo" assertions replaced).

Manual (recorded in the phase files as they pass):

- Does a `run_in_background` server survive the end of the Claude Code
  session? Record the result in `reference/revise.md`.
- Native Windows: two servers for one slug get two ports.
- WSL with a Windows browser, with the default and with
  `localhostForwarding=false`.
- The save flow in Chromium and Firefox.
- D19: revise and publish on a nearly finished presentation; grill,
  design, and build on the next new one.

Rollback: revert SPEC to `013023d` (or `2352685` for the 2026-10-07
design). serve.py is additive; the file-export + `pull_edits.py` path stays
in the code, so pointing `reference/revise.md` at the fallback disables it.
Template changes live in one file. The local.md migration only adds keys
and ignores old ones.

## Tickets (task graph)

T1–T13 cover the 2026-10-07 design.

| ID | Ticket | Blocked by |
|---|---|---|
| T1 | Scaffold: README, LICENSE, vendored frontend-slides files with MIT notice | — |
| T2 | `reference/brief-template.md`: BRIEF.md front matter (`phase`, slug, week, deck path) and the per-phase sections | — |
| T3 | `reference/local-template.md` + first-run questions (D16) | — |
| T4 | `templates/stage.html` from the author's stage-runtime deck: content removed, tokens on `:root`, section ids kept | T1 |
| T5 | `scripts/pull_edits.py`: generalize week04's script (any deck path, any export in Downloads, match by section id, notes included). Tests first | T4 |
| T6 | `scripts/publish.py`: copy + `cmp`, poll 200, live `cmp`, card grep. No git push inside. Tests first | T3 |
| T7 | `reference/grill.md` + `reference/context.md` (D7, D8, inline grilling) | T2 |
| T8 | `reference/build.md` + `reference/revise.md` (D9–D11, D17) | T2, T4, T5 |
| T9 | `reference/publish.md`: commit set, card drafting, push confirmation, DESIGN.md diff and extraction (D12–D14) | T2, T3, T6 |
| T10 | `SKILL.md` router + dependency detection (D2, D4, D6, D15, D19) | T7, T8, T9 |
| T11 | Dogfood on the author's nearly finished deck: revise + publish only | T10 |
| T12 | Template page on benjohnbill.github.io (D18) | T11 |
| T13 | Portability: downloads folder per OS, Python check, `python_cmd` in the docs (D20) | T10 |

T14–T28 cover the 2026-10-15 revision. Issue number = ticket number.

| ID | Ticket | Blocked by |
|---|---|---|
| T14 | `stage.html` part 1: derived tokens, template text, help overlay | — |
| T15 | BRIEF and local.md contracts: new keys, migration (D16, D23), generic examples, D24 guard | — |
| T16 | `scripts/serve.py`: revise server with three-way save. Tests first | T14 |
| T17 | `stage.html` part 2: served-mode save, autosave by id, banners | T16 |
| T18 | `publish.py`: Pages URL forms, `pages_dir`, assets, back-link depth, optional week. Tests first | T15 |
| T19 | `grill.md` + `context.md`: metadata round, `source_repo`, story frame, script, proposal rule | T15 |
| T20 | `reference/design.md`: design phase and getdesign mapping | T14, T15 |
| T21 | `build.md` + `revise.md`: Design section, assets, script to notes, server-based revise | T16, T17, T20 |
| T22 | `publish.md`: commit question, folder `.gitignore`, deploy question, D14 branch | T18 |
| T23 | `SKILL.md` router and README workflow tables | T19–T22 |
| T24 | Manual verification of the revision | T23 |
| T25 | `publish.py verify`: find the index card by a relative href | T18 |
| T26 | `publish.md`: one question, then commit and push together | T22 |
| T27 | `design.md`: accent contrast measured against `--paper` | T20 |
| T28 | `revise.md`: agent writes must not overwrite a student save | T21 |

## Open items

- License: MIT (decided 2026-10-07).
- Which file is the final presentation for the T11 run: the author decides at T11.
- Issue tracker for the tickets: GitHub Issues of `benjohnbill/jungle-deck` (see `docs/agents/issue-tracker.md`).
- Grilling record of the revision: `~/.claude/plans/jungle-deck-revision-2026-10-15/` (BRIEF, rounds, FINAL), on the author's machine only.
