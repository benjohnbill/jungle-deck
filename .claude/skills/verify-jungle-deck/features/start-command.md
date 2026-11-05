# The skill starts by slash command only

`SKILL.md` has `disable-model-invocation: true` (SPEC D2). A typed command starts the skill. Speech does not.

## Sub-features

- `slash-starts`: `/jdv:jungle-deck` runs the router and asks the first question.
- `speech-does-not-start`: "발표 자료 만들자" makes no `BRIEF.md` and asks no router question.
- `resume-line`: the session-break line names the command `/jungle-deck 이어서`.

## How to get to it (user POV)

- The student types `/jungle-deck`, as `README.md` says.
- The student says the old phrase in a fresh session.

## Driving it with jdv.py

Stage two runs at the revision. No persona card. Turn cap 1 per run.

1. `jdv.py turn <run-a> "/jdv:jungle-deck" --new`
2. `jdv.py turn <run-b> "발표 자료 만들자" --new`

Pass predicates:

- `slash-starts`: the reply of run A holds "이번 주 발표 자료를 어디에 저장할까요?". Quote it.
- `speech-does-not-start`: the reply of run B does not hold that question, and `find <run-b>/week09 -name BRIEF.md` prints nothing.
- `resume-line`: `grep "/jungle-deck 이어서" SKILL.md README.md` has a hit in each file.

## Gotchas

- Run B can still read the skill's files and tell the student to type the command. That is a pass: the skill did not start. Record the file reads as a cost.
- Measured 2026-11-05 at `a3418b5`: run A 175,316 cache read, run B 104,185. Speech costs tokens even though it does nothing.
- These sessions load the user's own `CLAUDE.md`, so the reply's voice is not the skill's voice. Do not judge the voice.
