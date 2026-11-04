# The repository is in a state that can be handed over

Before anyone says "done", the checkout, the remote, and CI must agree. It needs no `claude -p` run.

## Sub-features

- `tree-and-push`: no uncommitted file, and HEAD is on its upstream.
- `ci-truth`: CI on HEAD and on `main` is read from run conclusions, not from logs.
- `fresh-clone`: the tests pass with no untracked or ignored file.
- `names-in-history`: no protected name in any line ever added under `cases/`.

## How to get to it (user POV)

- The owner asks "다 끝났어?" before merging or before starting the next work.

## Driving it with repo_state.py

```
python3 tools/verify/repo_state.py --full
```

Pass predicates: each line is `PASS`. A `SKIP` is not a pass: report it with its reason. Save the output to `<scratch>/evidence/repo-state/`.

## Gotchas

- `CI on main` fails while a fix waits in an open PR. Report that as it is. It is not a reason to skip the line.
- `gh run view --log-failed` truncates. On 2026-11-05 it showed one failing test when three failed. Read run conclusions, and run the tests yourself for the list.
- A PR run tests the merge with `main`, not your branch. A local pass does not predict it when `main` has moved: `pushed` does not check that, so read `git log HEAD..origin/main`.
- `--full` takes about 90 seconds and opens a browser check in some tests. The clone is removed after the run.
