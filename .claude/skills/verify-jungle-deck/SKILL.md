---
name: verify-jungle-deck
description: Verify the jungle-deck skill the way a student uses it. Runs one revision of the skill in headless Claude Code sessions against a synthetic student repo, with you playing a scripted student persona, then judges the transcript. Use to prove that the skill follows the student's plan (no forced topic or flow), helps a student with a vague or empty plan, builds slides that match the plan, and uses fewer tokens than an older revision.
---

# Verify jungle-deck

The surface is a conversation: a student talks to Claude Code, and the skill
asks questions, reads the student's repo, and writes `BRIEF.md` and a slide
page. You drive it with `claude -p` and play the student. The rules under test
are in `SPEC.md` D7, D8, D9, D27 and `docs/adr/0001-ask-before-collecting-context.md`.

All commands run from the repo root. The helper is `tools/verify/jdv.py`
(`python3 tools/verify/jdv.py --help`). The judge is `tools/measure_run.py`.

## Launch

Stage one run directory per revision under your scratchpad:

```
python3 tools/verify/jdv.py stage <scratch>/runs/<feature>-<rev> <rev>
```

It writes `plugin/` (the skill at `<rev>` as the plugin `jdv`), the run's
`jungle-deck.local.md`, and `week09/` (a synthetic student repo: three commits
by the student `student@example.com`, one by a teammate, notes, and
`run_tests.py`). Ready when it prints `staged ...`. A staged directory is
never reused: stage a fresh one per run.

The student's first message is always `/jdv:jungle-deck`. Never use the bare
`/jungle-deck`: that is the installed copy and the user's own settings.

## Doctor

```
python3 tools/verify/jdv.py turn <run> "Which skills do you have whose name contains jungle-deck? Names only." --new
```

Pass when the reply lists `jdv:jungle-deck`. Then discard that run (it holds a
non-student session) and stage a fresh one. Also check `claude --version`
works and `git -C <run>/week09 log --oneline` shows 4 commits.

## Drive

One student turn:

```
python3 tools/verify/jdv.py turn <run> "<student message>"          # same session
python3 tools/verify/jdv.py turn <run> "<student message>" --new    # new session
```

It runs `claude -p` in `<run>/week09` with `--plugin-dir <run>/plugin`,
`--permission-mode acceptEdits`, the allowed tools `Bash Read Write Edit Glob Grep Skill`,
and nothing else: MCP tools (connectors, the user's browser) are listed but not
allowed, so `-p` refuses every call to them; never add one to the allowed list.
It resumes the last session, prints the reply, and appends the turn to
`<run>/state.json`.
A background task the skill starts (the revise server at the end of build)
keeps `claude -p` alive after the reply. `turn` then waits until the reply is
final and the transcript has been still for 30 s, stops the run's process
group (the server with it), and takes the reply from the transcript; the reply
ends with a `[jdv: ...]` line. Such a turn has no cost figure.

Play the student from the persona card in the feature file. Rules for you:

- Answer only from the card. Do not read the skill's files or the fixture
  repo to answer; the student knows only the card.
- Keep the card's facts fixed across revisions, so two runs compare. Adapt the
  wording to the question asked.
- When the skill offers a topic or a flow that is not on the card, say no and
  restate the card's plan. Record the quote: that is a finding.
- When it asks "새 세션에서 'jungle-deck 이어서'…", follow it with
  `turn ... "/jdv:jungle-deck jungle-deck 이어서" --new`.
- Cap each feature at the turn limit in its file. A run that hits the cap is
  a finding, not a pass.

Settings: the run's `jungle-deck.local.md` sits in the run directory and is
passed as `JUNGLE_DECK_CONFIG`, so the user's own settings are never read or
written. A revision before 2026-10-26 ignores that variable and reads the copy
in `plugin/skills/jungle-deck/`; there, Claude Code refuses its writes (a file
under a plugin is a sensitive file), and the skill says so in its reply. Do not
switch to `bypassPermissions` to get past it: that mode with a live agent is
refused, and it would open every tool. claude-mem is refused like every MCP
tool, so the skill skips that source (D15).

## Evidence

```
python3 tools/verify/jdv.py report <run> [<run> ...]
```

It prints, per run: sessions, student turns, cost, tokens (main cache read,
output, subagent cache read), the rule-check counts from
`tools/measure_run.py`, the `BRIEF.md` path and phase, and the built pages.
For per-session detail run `python3 tools/measure_run.py <transcript>`; the
transcript of each session is
`~/.claude/projects/<week09 path with every non-alphanumeric as ->/<session>.jsonl`.

Proof standards:

- Quote the skill's reply text for every question-shape claim (the opening
  question, the recall questions, a forced topic). `state.json` holds every
  reply.
- Read `BRIEF.md` for what was recorded. The student's words must be there.
- For a built page, run `python3 scripts/check_layout.py <page>`
  yourself; do not trust the transcript's claim.
- Token claims compare two runs of the same feature and persona at two
  revisions (`token-delta.md`). Never compare against a run on another repo
  or another persona.
- Copy `state.json`, the report output, and `BRIEF.md` into
  `<scratch>/evidence/<feature>-<rev>/` before cleanup.

## Cleanup

```
python3 tools/verify/jdv.py clean <run>
```

It stops only processes whose command line holds the run path (the revise
server that build starts). It removes nothing: the run directory and the
transcripts are the evidence. Delete a run directory only after its evidence
is copied. These sessions also run the user's own hooks (for example
claude-mem); say so in the report.

## Feature map

`features/README.md` is the index. Each feature file has a persona card, the
turn cap, and the pass predicates.
