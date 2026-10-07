---
name: jungle-deck
description: "Presentation deck for the weekly Krafton Jungle talk: settles the story with the student, builds a 2-minute HTML slide deck from this week's real debugging evidence, merges the student's browser edits, and publishes it to GitHub Pages. Resumes from BRIEF.md. Use when the student starts a deck (\"발표 덱\", \"발표 준비\", \"슬라이드 만들자\"), resumes one (\"jungle-deck 이어서\"), or publishes one (\"덱 게시\")."
---

# jungle-deck

A router. It finds the deck, reads its state, and hands the work to one
phase file. The phase files hold the rules; this file holds none of them.

All paths below are relative to the skill directory (the directory of this
file). `BRIEF.md` is the one exception: it lives in the deck folder,
`<week repo>/study/<deck-slug>/`.

## Steps

### 1. Load the personal settings

Read `jungle-deck.local.md` in the skill directory. When
`jungle-deck.local.md` is missing, this is the first run: run the Python
check, then ask the first-run questions, both in
`reference/local-template.md`, then write the file from its template.
Run the Python check also when `python_cmd` is empty or fails. Do this
before step 2.

Done when `jungle-deck.local.md` exists, you have read it, and
`python_cmd` holds a working command.

### 2. Find the deck

1. Find the week repo: the current git repo when it is a `weekNN/` repo.
   Else, look under `week_repo_root` from local.md and ask which week.
2. List `study/*/BRIEF.md` in the week repo.
3. Pick the deck:
   - The student names a topic or a slug: use that deck.
   - One BRIEF.md with `phase` other than `done`: use it.
   - More than one: ask which deck, as a numbered list.
   - No BRIEF.md, or the student asks for a new deck: make a new deck.
     Ask for the slug, create the folder, and copy the skeleton from
     `reference/brief-template.md`.

Done when you hold one BRIEF.md path.

### 3. Read BRIEF.md and dispatch

Read `BRIEF.md` first, before any other deck file. If no BRIEF.md exists,
start at `grill` (D6). Else read `phase` from its front matter and its
`Next action` section. Then read the phase file and follow it:

| `phase` | Phase file |
|---|---|
| `grill` | `reference/grill.md` (it also reads `reference/context.md`) |
| `build` | `reference/build.md` |
| `revise` | `reference/revise.md` |
| `publish` | `reference/publish.md` |
| `done` | Nothing to run. Give the live URL from the `Publish` section. For the next deck, go back to step 2 with `reference/brief-template.md` |

The resume and `phase` rules are in `reference/brief-template.md`
("How to resume", "Who changes `phase`"). Follow them at every phase.

## Dependencies

Each dependency is optional (D15). Detect it when a phase first needs it.
If it is present, use it. If it is absent, use the fallback and continue
the phase; the fallback is complete.

| Dependency (phase) | Detect | Fallback |
|---|---|---|
| `grilling` skill (grill) | The session's skill list names `grilling` | The inline rules in `reference/grill.md`, section "Grilling rules" |
| `frontend-slides` skill (build) | The skill list names `frontend-slides`, also as `frontend-slides:frontend-slides` | The vendored copies in `vendor/frontend-slides/` (MIT, upstream in `vendor/frontend-slides/SOURCE.md`) |
| `claude-mem` (grill, context) | A `claude-mem:mem-search` skill or an `mcp__plugin_claude-mem_*` search tool is available | Silently skip it as a context source |
| Pages settings (publish) | `pages_repo` in local.md is not empty | Stop after a finished local HTML: commit in the week repo, print the deck path. A `pages_repo` that is set but has no `.git` is an error, not the fallback: `scripts/publish.py copy` stops and names `pages_repo`. Ask the student to fix the path |

## Verification state

As of 2026-10-07: No phase has been verified on a real deck yet. The
phase files pass their contract tests in `tests/` only (D19).

- `revise` and `publish` are first verified on the first real deck (a
  nearly finished one).
- `grill` and `build` are first verified on the next new deck.

While a phase is unverified, treat its phase file as a draft. When a step
fails or does not fit the deck, stop, tell the student what failed, and
write it into `Next action` of BRIEF.md. Do not invent a replacement step.
After a phase works end to end on a real deck, update this section.
