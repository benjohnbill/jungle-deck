---
name: jungle-deck
description: "Build, resume, or publish the weekly Krafton Jungle 발표 자료 (2-minute HTML slides on GitHub Pages)."
disable-model-invocation: true
---

# jungle-deck

A router. It finds the presentation, reads its state, and hands the work to
one phase file. The phase files hold the phase rules. This file holds the
routing and one rule for every phase: "Words".

All paths below are relative to the skill directory (the directory of this
file). `BRIEF.md` is the one exception: it lives in the save folder of the
presentation, which the student chose when it was created.

## Words

The student hears Korean, and the thing is "발표 자료" in every question,
message, and suggested phrase. "덱" and "deck" stay in English documents,
file names, and code keys only. Story stages use the Korean words 도입,
전개, 전환, 마무리 (SPEC "Words": no Hanja). When he says "발표 덱" or
"덱 게시", answer with "발표 자료".

## Steps

### 1. Load the personal settings

Read `jungle-deck.local.md` at `$JUNGLE_DECK_CONFIG`, else
`~/.config/jungle-deck/jungle-deck.local.md` (see "Location" in
`reference/local-template.md`, which also moves an old copy from the skill
folder). When `jungle-deck.local.md` is missing, this is the first run: run the Python
check, then ask the first-run questions, both in
`reference/local-template.md`, then write the file from its template.
Run the Python check also when `python_cmd` is empty or fails. An older
file keeps working: apply "Migration" in the same reference. Do this
before step 2.

Done when `jungle-deck.local.md` exists, you have read it, and
`python_cmd` holds a working command.

### 2. Find the BRIEF

Follow "How to resume" in `reference/brief-template.md`. It holds these
hooks; do each one there:

- the search order and the `kind: jungle-deck` check;
- "Migration from the old format" (D23);
- a new presentation: the save folder, the skeleton, and the
  `current_brief` and `prev_brief` updates in local.md.

Done when you hold one BRIEF.md path, already migrated, or you started a
new one from the skeleton.

Until the student answers the opening question of `grill`, read only
`BRIEF.md` files and `jungle-deck.local.md` (D8). For `source_repo`, run
`git rev-parse --show-toplevel` and nothing else: no `git log`, no repo
files, before the student answers the opening question.

### 3. Read BRIEF.md and dispatch

Read `BRIEF.md` first, before any other file of the presentation. A new
BRIEF.md has `phase: grill`: with no BRIEF.md, you start at `grill` (D6). Read `phase` from its front
matter and its `Next action` section. Then read the phase file and follow
it:

| `phase` | Phase file |
|---|---|
| `grill` | `reference/grill.md` (it also reads `reference/context.md`) |
| `design` | `reference/design.md` |
| `build` | `reference/build.md` (its finish starts the revise server) |
| `revise` | `reference/revise.md` (server, save loop, file fallback) |
| `publish` | `reference/publish.md` (its own numbered steps, commit to live check) |
| `done` | Nothing to run. Give the live URL from the `Publish` section. For a new presentation, follow "How to resume" step 3 in `reference/brief-template.md` |

A BRIEF at `design` or later skips grilling (D6). Moving `phase` follows
"Who changes `phase`" in `reference/brief-template.md`, at every phase.

### 4. Suggest one session break

When `phase` moves from `design` to `build`, send this line once, after the
BRIEF.md edit: "새 세션에서 'jungle-deck 이어서'라고 하면 가볍게 이어져요.
여기서 계속하려면 '계속'이라고 해 주세요." Then end your turn: do not start
`build` in the same turn. Build starts here only when the student says to go
on here. It is a suggestion, not a gate. Never repeat it (D27).

## Dependencies

Each dependency is optional (D15). Detect it when a phase first needs it.
If it is present, use it. If it is absent, use the fallback and continue
the phase; the fallback is complete.

| Dependency (phase) | Detect | Fallback |
|---|---|---|
| `grilling` skill (grill) | The session's skill list names `grilling` | The inline rules in `reference/grill.md`, section "Grilling rules" |
| `frontend-slides` skill (design, build) | The skill list names `frontend-slides`, also as `frontend-slides:frontend-slides` | The vendored copies in `vendor/frontend-slides/` (MIT, upstream in `vendor/frontend-slides/SOURCE.md`) |
| `claude-mem` (grill) | A `claude-mem:mem-search` skill or an `mcp__plugin_claude-mem_*` search tool is available | Silently skip it as a context source |
| `gh` (grill, publish) | `gh auth status` succeeds | Public REST API for a public repo, no Project board (`reference/grill.md`); ask for the Pages source folder (`reference/publish.md`) |
| Revise server (revise) | `scripts/serve.py` starts and the student's browser reaches its address | File export and `scripts/pull_edits.py`: "Fallback: no server" in `reference/revise.md` |
| Headless browser (build, revise) | `scripts/check_layout.py` does not exit 3 (it finds Chrome, Chromium, or Edge) | Skip the layout check; the student preview is the check |
| `Monitor` tool (revise) | The session's tool list has `Monitor` | The student tells you after each save |
| Pages target (publish) | The student says yes to a GitHub Pages deploy, and `pages_repo` in local.md is not empty after the setup step | Stop after a finished local HTML and print its path. A `pages_repo` that is set but has no `.git` is an error, not the fallback: `scripts/publish.py copy` stops and names `pages_repo`. Ask the student to fix the path |

## Verification state

As of 2026-11-04, by the author's report: every phase ran on a real
presentation before the figures change of 2026-10-29.

The figures change has not run on a real presentation. It covers the `Show`
line in `reference/grill.md`, "Figures" in `reference/build.md`, and
`vendor/diagram-design/`.

Treat the figures change as a draft. When one of its steps fails or does not
fit the presentation, stop, tell the student what failed, and write it into
`Next action` of BRIEF.md. Do not invent a replacement step. When a manual
check passes, record it in its phase file. When the figures change works end
to end on a real presentation, update this section.
