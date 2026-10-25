# Slides match the student's intent

The page that build writes must carry the student's plan, use real output, and
fit the screen, with one layout check and no screenshot loop.

## Sub-features

- `carry-the-plan`: the slides follow the recorded story frame and theses.
- `real-evidence`: evidence on the slides is output of `run_tests.py` saved in `evidence/`.
- `one-check`: build runs `scripts/check_layout.py` and no self-made screenshot tool.
- `session-break`: one suggestion of a new session at design → build.

## How to get to it (user POV)

- Continue the `clear-plan` persona through design and build.

## Driving it with jdv.py

Persona card: the `clear-plan` card, plus:

- Design: no reference, no getdesign.md; pick the first preview; keep the accent.
- After build: "브라우저로 봤어요. 좋아요".

Steps:

1. Run `clear-plan` on a fresh run, then answer "네" to the design question.
2. Answer design from the card. When the session-break line appears, run `turn <run> "/jdv:jungle-deck jungle-deck 이어서" --new`.
3. Let build finish. Answer the draft question from the card. Stop when `phase` is `revise`.
4. Run `jdv.py clean <run>`.

Pass predicates:

- `carry-the-plan`: each `Slide theses` row of `BRIEF.md` has a `<section id>` in the page, in order; the title slide states the takeaway or the bug lead-first. Quote the title.
- `real-evidence`: every log on a slide appears verbatim in a file under `evidence/`, and that file's command is `run_tests.py` (or a `git` command).
- `one-check`: `check_layout_runs` ≥ 1 and `screenshot_tool_calls` 0 across both sessions. Run `scripts/check_layout.py <page>` yourself: exit 0, or exit 1 with the finding recorded in `Open issues for revise`.
- `session-break`: `session_break_lines` is exactly 1 across both sessions.

## Gotchas

- Build starts the revise server; always run `jdv.py clean` after.
- The fixture has no images. An image slide is not expected.
