---
name: audit-jungle-deck
description: Audit the jungle-deck repository as its owner, with no student session. Checks that the checkout, the remote, CI, and a fresh clone agree, and that public files under cases/ hold no private facts and match their source decks. Use before a merge or a push to main, before saying the work is done, after adding a case, or when asked whether the repository is ready to hand over. To test how a student meets the skill, use verify-jungle-deck.
---

# Audit jungle-deck

The surface is the repository, not a conversation. Nothing here runs `claude -p`. All commands run from the repo root.

## Launch

Nothing to start. The audit reads the checkout. Save evidence under `<scratch>/evidence/<feature>/`.

## Doctor

```
python3 tools/check_cases.py
gh auth status
```

`check_cases.py` must print `ok`. Without `gh`, the CI and PR lines of `repo_state.py` print `SKIP`. A `SKIP` is not a pass: report it.

## Drive

Every time:

```
python3 tools/verify/repo_state.py --full
```

After a change under `cases/`, also follow `features/public-safe.md`.

## Evidence

- Save the `repo_state.py` output as it printed. Quote each `FAIL` and `SKIP` in the report.
- Read CI from run conclusions, not from logs.
- For a reading finding, quote the file and the line.
- CI already runs `tools/check_cases.py` through `tests/test_cases.py`. A green CI does not replace the reading pass, because the scan knows only its list.

## Cleanup

`repo_state.py` removes its own clone. A reader agent writes nothing. Delete a planted copy from `public-safe`. Keep the evidence.

## Feature map

| Feature | What it proves | When |
|---|---|---|
| [repo-state](features/repo-state.md) | Checkout, remote, CI, and a fresh clone agree | Before a merge, and before saying done |
| [public-safe](features/public-safe.md) | Public case files hold no private fact and match their source | After a change under `cases/` |
