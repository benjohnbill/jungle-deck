# Token delta between two revisions

Proves the token claim: the same persona on the same fixture costs less on the
new revision than on the old one.

## Sub-features

- `same-scenario`: both runs use one feature, one persona card, one fixture.
- `delta`: main cache read, output, and subagent cache read, old against new.
- `where`: which phase the difference comes from.

## How to get to it (user POV)

- Not a user path. It is two runs of one feature file, at two revisions.

## Driving it with jdv.py

1. Pick the feature: `slides-match-intent` for the full claim, `clear-plan` for grill only (cheaper).
2. Stage `<scratch>/runs/<feature>-old` at `9454a0c` (the last revision before 2026-10-25) and `<scratch>/runs/<feature>-new` at `HEAD`.
3. Run the feature on old, then on new. Never run both at once: they share the user's hooks and rate limits.
4. `python3 tools/verify/jdv.py report <old run> <new run>`.
5. For the phase split, run `python3 tools/measure_run.py <transcript>` per session and compare `cache read by phase`.

Pass predicates:

- `same-scenario`: both `state.json` files show the same persona answers for the same questions (where the questions differ by revision, the same card facts).
- `delta`: new main cache read + subagent cache read is lower than old. Report the ratio and the absolute numbers.
- `where`: name the phase with the largest drop, and check it against the change that should cause it (grill: no subagents and scoped reads; build: one layout check; the session break).

## Gotchas

- Explain the number before trusting it. A run that stopped early, hit the cap, or skipped a phase is cheaper for the wrong reason: check that both runs reached the same phase (`jdv.py report` prints it).
- The old revision proposes topics first; the persona then restates its plan, which adds turns. That cost is part of the old behavior, keep it.
- A simulated student answers at once and never wanders, so both totals are far below a real week (the week08 run: 26.49M main cache read plus 13.19M in subagents). Compare the two runs, not either run against week08.
