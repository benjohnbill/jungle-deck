---
scope: What the jungle-deck skill does and how it is built
authority: Design settled by a grilling session with the user, 2026-10-07 (Q1–Q27). Decisions here are the user's; change them only with the user
status: confirmed 2026-10-07; implemented on main (tickets T1–T10), T11–T12 open
---

# jungle-deck — spec

A Claude Code skill for Krafton Jungle students. It takes a student from
"I have a troubleshooting story this week" to a published 2-minute HTML
slide deck. It is built on the `frontend-slides` skill and adds the Jungle
context, a resumable phase file, real tool evidence, and a publish step.

Reference style for the author's own decks:
`~/dev/krafton-jungle/docs/slides/DESIGN.md` (Plex Swiss Grid). That file
is personal. The skill does not ship it.

## Users

- **The author** (benjohnbill). Uses the skill weekly, with personal
  settings in `jungle-deck.local.md`. Same code path as everyone else.
- **Other Jungle students.** Clone the public repo into
  `~/.claude/skills/jungle-deck`. They may not have `frontend-slides`,
  `grilling`, `claude-mem`, or any GitHub Pages site.

## Decisions

| # | Decision |
|---|---|
| D1 | One skill, name `jungle-deck`. Source: `~/dev/krafton-jungle/skills/jungle-deck/`, its own git repo, public remote `benjohnbill/jungle-deck`. Installed by symlink into `~/.claude/skills/`, like `jungle-close` |
| D2 | Triggers: "발표 덱", "발표 준비", "슬라이드 만들자", "jungle-deck 이어서", "덱 게시", and `/jungle-deck` |
| D3 | Phases: `grill → build → revise → publish`. No rehearsal phase |
| D4 | State lives in `BRIEF.md`, never only in the conversation. Its front matter holds `phase:`. On every call the skill reads BRIEF.md and resumes at that phase. A finished phase is skipped. BRIEF.md replaces handoff documents |
| D5 | Deck folder: `<week repo>/study/<deck-slug>/` holds `BRIEF.md`, `<deck-slug>.html`, and `evidence/` (repro sources, tool logs) |
| D6 | Calling the skill assumes design may already be done. With no BRIEF.md, start at `grill`. With a BRIEF.md at `build` or later, skip grilling |
| D7 | `grill` settles six things: (1) the one-sentence conclusion, lead-first, and the closing line; (2) the story frame (起承轉結 7 slides, or symptom → evidence → cause 6 slides); (3) one thesis sentence per slide, **written by the student**; (4) the evidence list: which real output goes on which slide; (5) the accent / style variation; (6) terms the audience may not know, to define on screen. The agent proposes candidates for 1, 2, 4, 5, 6; the student chooses |
| D8 | Context collection runs at the start of `grill`, always: `git log` of the week repo, its README and notes, the progress memo if one exists. `claude-mem` is used only when installed |
| D9 | `build` uses a stage-runtime template (derived from the author's own stage-runtime deck, content removed): fixed slides, one active, `#N` hash, per-element `data-step`, speaker notes on `N`, in-browser edit mode on `E`, `Ctrl+S` export. Speaker notes are a light suggested script only |
| D10 | The 2-minute limit is background, not a gate. No timer check. Do not cut content only to fit a timer |
| D11 | `revise` is the main loop. The student edits in the browser and exports; a script merges the export back into the source by `<section id>`; the agent then adjusts layout and evidence to match. Repeat until the student says to publish. The merge-back script is required |
| D12 | `publish`: commit the deck, BRIEF.md, and `evidence/` in the week repo. Copy the deck to `<pages repo>/study/weekNN/<deck-slug>.html` and verify with `cmp`. Draft the index card from BRIEF.md. Commit in the Pages repo. Ask the student once, then push both repos. Poll until the deck URL returns 200, `cmp` the live page, and grep the index for the card URL. Edit only the source, never the copy. Existing published decks keep their URLs |
| D13 | `.gitignore` in the deck's week repo: `_backup/`, `previews/`, `.impeccable/` |
| D14 | Design feedback: at `publish`, show what this deck changed against the student's DESIGN.md as a diff; apply only the items the student picks. With no DESIGN.md, offer to extract one from this deck (Google Labs DESIGN.md format), and record its path in local.md. Later decks then skip style discovery |
| D15 | Dependencies: use it if present, else a built-in fallback. `grilling` → inline round rules. `frontend-slides` → vendored files with the MIT notice. `claude-mem` → skip. No publish settings → stop after a finished local HTML |
| D16 | Personal settings: `jungle-deck.local.md` in the skill directory, gitignored. Fields: display name, week-repo root, Pages repo path and URL base, card format, DESIGN.md path, preferred accent. If missing, the first run asks a few questions and writes it. The author uses it too |
| D17 | Style: first deck uses frontend-slides style discovery (Phase 2). After that, the DESIGN.md from D14 |
| D18 | Template page: one fixed page pinned at the top of `benjohnbill.github.io`, no week or topic. It holds the phase diagram, the one-line install, the first-run questions, the author's three decks as examples, and links to `frontend-slides` and the skill repo. Built only after the skill works and the publish path is verified |
| D19 | Verification state is written into the skill: the first real use (a nearly finished deck) verifies only `revise` and `publish`. `grill` and `build` are first verified on the next new deck |

## Shared Jungle context (ships in the skill)

From the user's own words (sessions 2026-09-16 to 2026-10-07):
weekly Thursday talk; troubleshooting from this week's work in a refined,
WIL-like, lead-first form; audience = cohort studying C together, wide level
spread, more than half know the topic; Korean; 2 minutes, no Q&A; large
monitor in a bright lecture room; an experiment / debugging story is
preferred; the deck also feeds the student's WIL. Speaker, publishing, and
style rows are personal and live in local.md.

## Repository layout (target)

```
jungle-deck/
├─ SKILL.md                 # router: triggers, read BRIEF, dispatch phase, dependency checks
├─ README.md                # install, first run, credits
├─ LICENSE
├─ SPEC.md                  # this file
├─ reference/
│  ├─ context.md            # shared Jungle context
│  ├─ brief-template.md     # BRIEF.md skeleton + phase contract
│  ├─ grill.md              # D7, D8, inline grilling rules
│  ├─ build.md              # D9, D10, D17
│  ├─ revise.md             # D11
│  ├─ publish.md            # D12–D14, card format
│  └─ local-template.md     # D16 fields and first-run questions
├─ templates/stage.html     # D9
├─ scripts/
│  ├─ pull_edits.py         # D11, generalized from week04/study/pull-edits.py
│  └─ publish.py            # D12 copy, cmp, poll, card grep (no push)
├─ vendor/frontend-slides/  # viewport-base.css etc. + MIT LICENSE
└─ .gitignore               # jungle-deck.local.md
```

## Tickets (task graph)

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

## Open items

- License: MIT (decided 2026-10-07).
- Which file is the final deck for the T11 run: the author decides at T11.
- Issue tracker for the tickets: none set up yet.
