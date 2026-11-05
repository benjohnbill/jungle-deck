# Cases are read only on request

`cases/` holds finished talks (SPEC D28). The skill must not offer them first, must not read them unprompted, and must record a pick so that `build` uses it.

## Sub-features

- `not-offered`: a student who does not ask never hears about `cases/`, and no `cases/` file is read.
- `index-first`: on request, the skill reads `cases/INDEX.md`, and shows two or three rows with `preview.png` paths.
- `base-recorded`: a pick writes `Source: cases/<case>/DESIGN.md` and the mapped tokens.
- `borrow-recorded`: a borrowed part writes `Figures from: cases/<case>/DESIGN.md § <part>`, and the tokens stay the base's.
- `brief-gated`: no case `BRIEF.md` is read until the student asks how that talk was planned.
- `case-read-only`: no file under `plugin/skills/jungle-deck/cases/` changes.

## How to get to it (user POV)

- At the `design` questions, the student says "빠르게 참고할 디자인 있어?".
- The student says "week07 사례를 참고해 줘".

## Driving it with jdv.py

Persona card A (`not-offered`): the `clear-plan` card. At the design question, the student names no reference and asks for no case. Stop when `phase` is `build`. Turn cap 16.

Persona card B (the other sub-features): the `clear-plan` card, plus these lines:
- "참고할 디자인을 빠르게 보고 싶어요."
- "week07-circular-list로 할게요. Branch graph는 week08 것을 쓰고 싶어요."
- At the end of design: "그 발표는 어떻게 기획했어요?"

Stop when `phase` is `build`. Turn cap 18.

Read the file calls from the transcript (`jdv.py report` names the sessions, and `SKILL.md` § Evidence gives the path).

Pass predicates:

- `not-offered`: in run A, no reply holds `cases/` or 사례, and no `Read`, `Grep`, `Glob`, or `Bash` call touches a path under `cases/`. `BRIEF.md` is written from the template, so a `Write` that holds the hint `cases/<case>/DESIGN.md` is expected.
- `index-first`: in run B, the first `cases/` read is `cases/INDEX.md`, and it comes before any case `DESIGN.md`. Quote the rows shown.
- `base-recorded`: `BRIEF.md` § Design has the `Source` line, and `Tokens` holds `#ff3300`.
- `borrow-recorded`: `BRIEF.md` § Design has the `Figures from` line with a part name that `cases/INDEX.md` lists. `Tokens` did not change after the borrow.
- `brief-gated`: the first read of a case `BRIEF.md` comes after the student's planning question.
- `case-read-only`: `diff -r <run>/plugin/skills/jungle-deck/cases <repo>/cases` prints nothing.

## Gotchas

- A card that says "타임라인" with week08 finds no such part, and the skill says so. Week08 calls it `Branch graph`. Measured 2026-11-05. The skill was right to refuse: keep the part name on the card.
- The accent question still runs after the pick. Answer it from the card, not as a finding.
- A reply that names getdesign.md for a case request is a FAIL for `index-first`: cases are separate from it.
