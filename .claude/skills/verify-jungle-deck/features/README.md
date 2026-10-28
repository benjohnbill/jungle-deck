# jungle-deck verification map

The maintained source for verifying jungle-deck as a student meets it. Read
`../SKILL.md` first; it holds Launch, Drive, Evidence, and Cleanup.

| Feature | What it proves | Turn cap |
|---|---|---|
| [clear-plan](clear-plan.md) | A student with a topic and a flow keeps both; nothing is forced | 14 |
| [vague-plan](vague-plan.md) | A student with only a fuzzy idea gets help inside that idea | 14 |
| [no-plan](no-plan.md) | A student with nothing gets the meta round, not a topic list | 10 |
| [slides-match-intent](slides-match-intent.md) | The built page carries the student's plan and fits the screen | 30 |
| [figures-legible](figures-legible.md) | Each figure shows its `Show` line only, reads at slide size, and reveals in steps | 30 |
| [token-delta](token-delta.md) | The new revision uses fewer tokens than the old one on the same persona | per feature |

## Baseline preconditions

- A fresh run directory from `jdv.py stage` per run. Never reuse one.
- The fixture student is `student@example.com`. The fixture week is the
  stack-growth bug in `vm/stack.c` (see `HISTORY` in `tools/verify/jdv.py`).
- `claude` on `PATH`, logged in. Chrome, Chromium, or Edge for the layout check
  (exit 3 from `check_layout.py` means none; record it).

## Proof and skip reporting

- Every predicate is PASS or FAIL with a quote from `state.json`, a line from
  `jdv.py report`, or a file path. An impression is not evidence.
- A predicate the run could not reach (the cap was hit, the skill stalled)
  is FAIL with the last reply quoted.
- The judgement "did the student feel forced?" stays with a human. These
  features prove the observable half: what the skill asked, read, proposed,
  and recorded.
