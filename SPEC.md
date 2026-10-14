---
scope: What the jungle-deck skill does and how it is built
authority: Design settled by grilling sessions with the user: 2026-10-07 (Q1–Q27) and 2026-10-15 (Q1–Q30, from real users' feedback). Decisions here are the user's; change them only with the user
status: revised 2026-10-15; the revision is not implemented. main implements the 2026-10-07 design (tickets T1–T10, T13). Next step: an agent-grilling challenge of this revision, then tickets
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
  any GitHub Pages site, or a `weekNN/` directory layout.

## Words

- **User-facing speech is Korean and says "발표 자료"**, never "덱" or
  "deck". Questions, messages, trigger phrases the skill offers, and the
  card badge follow this. The skill name `jungle-deck`, English documents,
  file names, and code keys (`deck:`, `data-kind="deck"`) stay as they are.
- **No Hanja in user-facing speech.** Story stages are named 도입, 전개,
  전환, 마무리.

## Decisions

| # | Decision |
|---|---|
| D1 | One skill, name `jungle-deck`. Source: `~/dev/krafton-jungle/skills/jungle-deck/`, its own git repo, public remote `benjohnbill/jungle-deck`. Installed by symlink into `~/.claude/skills/`, like `jungle-close` |
| D2 | Triggers: "발표 자료 만들자", "발표 준비", "슬라이드 만들자", "jungle-deck 이어서", "발표 자료 게시", and `/jungle-deck`. The old phrases "발표 덱" and "덱 게시" still trigger the skill, but the skill does not use them in its own speech |
| D3 | Phases: `grill → design → build → revise → publish → done`. No rehearsal phase |
| D4 | State lives in `BRIEF.md`, never only in the conversation. Its front matter holds `phase:`. On every call the skill reads BRIEF.md and resumes at that phase. A finished phase is skipped. BRIEF.md replaces handoff documents |
| D5 | Save location: when a new presentation starts, the skill asks "이번 주 발표 자료를 어디에 저장할까요?". Default: `<current directory>/<slug>/`. The folder holds `BRIEF.md`, `<slug>.html`, and `evidence/`. The folder need not be in a git repo. To resume, the skill looks for `BRIEF.md` under the current directory first, then at `last_brief` in local.md. No `weekNN/` layout is assumed |
| D6 | Calling the skill assumes design may already be done. With no BRIEF.md, start at `grill`. With a BRIEF.md at `design` or later, skip grilling |
| D7 | `grill` settles the content, in this order. (1) Context collection (D8), no questions. (2) Context check-in (D8) and four metadata items in the same round: what to present (the agent proposes 2–3 sharpened candidates from what the student said or from the context), why, the one line the audience should take away, and the slide count (suggest 6 ± 2; a suggestion, not a rule). The takeaway line steers the grilling; it need not appear on a slide. (3) Story frame, as two questions: the structure — 오프닝 → 도입 → 전개 → 전환 → 마무리 (storytelling; recommended) or 증상 → 증거 → 원인 — and the opening — common ground (it may link to last week's topic, read from the previous BRIEF.md at `last_brief`) or a plain topic introduction with the student's motive. A frame fixes no slide count. (4) The lead-first title slide and the closing line. (5) One thesis per slide. (6) The evidence list. (7) Terms to define on screen. (8) Script, optional: "발표 스크립트를 먼저 만들까요?" — yes: the agent drafts a full per-slide script that tells the story, with a 2-minute speaking length (about 600–700 syllables) as guidance only (D10); the confirmed script becomes the speaker notes in build. No: build writes light notes. (9) "이 내용으로 디자인을 정할까요?" before `phase` moves to `design`. For every item the agent proposes candidates or drafts actively and recommends one; the student picks or rewrites. BRIEF.md records only the student's final wording |
| D8 | Context collection runs at the start of `grill`, always. Sources, in order: the local git repo of the save location — `git log` and the files this week's commits touched; the study-notes site at `notes_url`; with `gh` installed and logged in, the repo's issues, PRs, and Project board; without `gh`, a public repo's issues and PRs through the unauthenticated GitHub REST API (60 requests per hour); `claude-mem` only when installed. The GitHub Project board needs `gh` (GraphQL requires auth). The check-in message then shows what was found and what could not be read, and asks: "이 로컬 저장소를 기준으로 보면 될까요?", whether other sources exist, and whether there is more the agent should know. If `notes_url` cannot be read (for example a private Notion page), ask the student to paste or export the page |
| D9 | `build` uses a stage-runtime template (derived from the author's own stage-runtime deck, content removed): fixed slides, one active, `#N` hash, per-element `data-step`, speaker notes on `N`, in-browser edit mode on `E`, save on `Ctrl+S`. Build reads the style only from the `Design` section of BRIEF.md. Speaker notes are the confirmed script (D7 item 8) or a light suggested script. Usage guidance: at the end of build, three lines in the terminal (how to open, the keys, what to do after an edit); in the page, a `?` key shortcut overlay and a one-time hint on first open. Both say "고친 뒤 저장하고 에이전트에게 말해 주세요" |
| D10 | The 2-minute limit is background, not a gate. No timer check. Do not cut content only to fit a timer. Slide-count and script-length numbers are suggestions |
| D11 | `revise` is the main loop. The agent starts `scripts/serve.py` (stdlib only, bound to `127.0.0.1`) and the student opens the presentation through it. Save in the page writes straight into the source file: the server applies the `pull_edits` merge by `<section id>`, keeps a backup, writes atomically, and prints one log line per save. Default flow: the student saves, then tells the agent ("저장했어, 봐줘"); the agent reads the diff and adjusts layout and evidence. Where the Claude Code `Monitor` tool works, the agent may also watch the log and react on its own. No in-page request notes. Fallback without the server (page opened as a file): `Ctrl+S` exports to the downloads folder and `scripts/pull_edits.py` merges it. The server must reject requests from other origins (custom-header or `Origin` check), and must reject any path outside the presentation folder |
| D12 | `publish`: if the save location is in a git repo, commit the presentation, BRIEF.md, and `evidence/` by name. Then ask "이 발표 페이지를 따로 배포할 생각이 있어요?". No: stop at the local HTML and print its path. Yes: GitHub Pages is the only automated target; ask for the local Pages repo path then and record it as `pages_repo` (with `pages_repo` already set, ask "지난번처럼 `<path>`에 배포할까요?"). Another host: print the HTML path and stop. Copy to `<pages_repo>/study/weekNN/<slug>.html` when the week is known, else `<pages_repo>/study/<slug>.html`, and verify with `cmp`. Add the index card and keep the page's back-to-index link only when `<pages_repo>/index.html` exists and holds card markup of the built-in shape (`class="card"` with `data-week`); else skip the card silently and remove the back link. Commit in the Pages repo. Ask once, then push. Poll until the URL returns 200, `cmp` the live page, and grep the index for the card URL when a card was added. Edit only the source, never the copy. Existing published pages keep their URLs |
| D13 | `.gitignore` in the git repo of the save location, when it is one: `_backup/`, `previews/`, `.impeccable/` |
| D14 | Design feedback: at `publish`, show what this presentation changed against the student's DESIGN.md as a diff; apply only the items the student picks. With no DESIGN.md, offer to extract one from this presentation (Google Labs DESIGN.md format), and record its path in local.md. Later presentations then confirm it in `design` |
| D15 | Dependencies: use it if present, else a built-in fallback. `grilling` → inline round rules. `frontend-slides` → vendored files with the MIT notice. `claude-mem` → skip. `gh` → public REST API for public repos; skip the Project board. `Monitor` → the student tells the agent after each save. No publish target → stop after a finished local HTML |
| D16 | Personal settings: `jungle-deck.local.md` in the skill directory, gitignored. Fields: display name, study-notes site (`notes_url`), DESIGN.md path, preferred accent, downloads folder, Python command, last BRIEF path (`last_brief`), Pages repo path and URL base (written at publish, D12), card format. `week_repo_root` is removed. First run asks: display name, study-notes site, DESIGN.md path, preferred accent, downloads folder. Migration: an existing file keeps working; `week_repo_root` is ignored; a key that is missing (not empty) is asked once on the next run; an empty value `""` is a valid answer and is never asked again |
| D17 | `design` phase, between `grill` and `build`. (1) With `design_md` set: "이번에도 이 스타일로 갈까요?" — yes: confirm the accent, then done. (2) Else, or no: ask "원하는 디자인 레퍼런스가 있어요? (사이트 URL, 이미지, DESIGN.md)" and "getdesign.md 레퍼런스 중에서 고를까요?". (3) Style source, first that applies: the student's reference > a getdesign.md pick (D25) > `frontend-slides` style discovery > vendored presets. (4) Two or three previews, the student picks, then the accent. (5) Record source, tokens, and accent in the `Design` section of BRIEF.md. Move to `build` only on the student's confirmation |
| D18 | Template page: one fixed page pinned at the top of `benjohnbill.github.io`, no week or topic. It holds the phase diagram, the one-line install, the first-run questions, the author's three presentations as examples, and links to `frontend-slides` and the skill repo. Built only after the skill works and the publish path is verified |
| D19 | Verification state is written into the skill. The first real use verified nothing end to end yet. After this revision, `grill` and `design` are unverified drafts; `revise` and `publish` are first verified on a nearly finished presentation, `grill`, `design`, and `build` on the next new one |
| D20 | Portability (2026-10-07): the skill runs on macOS, Windows, Linux, and WSL. The downloads folder default is detected per OS, and the student confirms it into `downloads_dir`; on WSL with no answer, ask, do not guess. Python 3.8 or later: the first run tries `python3`, `python`, `py -3` and records the first that works as `python_cmd`. Check again only when it is empty or fails. Never install Python |
| D21 | The week number is optional. Read it silently from a `week\d+` part of the save path into BRIEF.md `week:`; never ask for it. With no week: the title slide drops its week line, `publish.py --week` is omitted, and the Pages path has no week folder |
| D22 | Shared context is general (see the next section). It must hold for C weeks, Pintos weeks, and the later Python and AI weeks. Evidence is real output the student ran — test results or terminal logs — never invented, and not tied to a named toolchain |
| D23 | An existing BRIEF.md in the old format: at `phase: grill`, add each new slot (metadata, story frame questions, title slide, script, design) as `TBD` and keep the filled slots. At `build` or later, do not change it. The old `Conclusion` slot maps to the title slide |
| D24 | No author-specific examples ship as defaults. SPEC, `reference/local-template.md`, and the other reference files use generic example values, not the author's paths and sites |
| D25 | getdesign.md references (VoltAgent `awesome-design-md`, MIT, Google DESIGN.md format): list the brands from the repo through raw GitHub URLs; no `npx`. Recommend 2–3 by mood and link each preview at `getdesign.md/<brand>/design-md`. A brand that is not in the repo: the student downloads it from the site and gives the path. Mapping into `stage.html` `:root`: canvas → `--paper`, ink → `--ink`, primary → `--acc`, ink-mute → `--mut`, hairline → `--grid`, canvas-soft → `--panel`; font family only, with a Korean font appended and a note when a paid font falls back to a system font; keep the template's `clamp()` sizes and take only weight, letter spacing, and line height; drop components and decorative signatures. When the agent proposes a reference, it says first that only the color and type mood transfer, and points to `frontend-slides` presets for a full slide style |
| D26 | README holds the whole workflow as tables: per phase, what the skill asks and what the student decides |

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

## Repository layout (target)

```
jungle-deck/
├─ SKILL.md                 # router: triggers, read BRIEF, dispatch phase, dependency checks
├─ README.md                # install, first run, workflow tables (D26), credits
├─ LICENSE
├─ SPEC.md                  # this file
├─ reference/
│  ├─ context.md            # shared Jungle context (D22)
│  ├─ brief-template.md     # BRIEF.md skeleton + phase contract
│  ├─ grill.md              # D7, D8, inline grilling rules
│  ├─ design.md             # D17, D25
│  ├─ build.md              # D9, D10
│  ├─ revise.md             # D11
│  ├─ publish.md            # D12–D14, card format
│  └─ local-template.md     # D16 fields, first-run questions, migration
├─ templates/stage.html     # D9
├─ scripts/
│  ├─ pull_edits.py         # D11 merge by section id
│  ├─ serve.py              # D11 local server: save straight to source
│  ├─ downloads_dir.py      # D20 downloads folder per OS
│  └─ publish.py            # D12 copy, cmp, poll, card grep (no push)
├─ tests/                   # unittest; contract tests for the reference files
├─ vendor/frontend-slides/  # viewport-base.css etc. + MIT LICENSE
└─ .gitignore               # jungle-deck.local.md
```

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

Tickets for the 2026-10-15 revision are cut after the agent-grilling
challenge settles it.

## Open items

- License: MIT (decided 2026-10-07).
- Which file is the final presentation for the T11 run: the author decides at T11.
- Issue tracker for the tickets: GitHub Issues of `benjohnbill/jungle-deck` (see `docs/agents/issue-tracker.md`).
- For the agent-grilling challenge: the security of `scripts/serve.py` (bind address, origin check, path escape) needs a focused review.
