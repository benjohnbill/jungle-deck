# Public case files hold no private facts, and match their source

`check_cases.py` catches only the names on its list. This feature is the reading pass that the list cannot do. It needs no `claude -p` run.

## Sub-features

- `name-list-works`: the scan finds a planted name.
- `unlisted-names`: a fresh reader finds no person, team repo, or private link outside the list.
- `images-clean`: no `preview.png` shows a name.
- `records-true`: a public `BRIEF.md` keeps the facts of its source.
- `parts-real`: each part in a `DESIGN.md` comes from its source deck.

## How to get to it (user POV)

- A stranger reads `cases/` on GitHub. A teammate searches for their own name.

## Driving it with a reader agent

Spawn one read-only reader per case with a fresh context, and give it the case folder and these questions. Do not give it the name list: it must find names without it.

Sources: the published decks are the links in `README.md`. Ask the owner for any deck that is not there, and for the private `BRIEF.md` files. Do not write those paths into a tracked file (D24).

Pass predicates:

- `name-list-works`: copy a case folder to scratch, append the output of `git config user.name` to its `BRIEF.md`, and run `python3 tools/check_cases.py <copy>`. It reports that line. Delete the copy.
- `unlisted-names`: the reader lists every proper noun in `DESIGN.md` and `BRIEF.md`, and classifies each as a public project, a tool, or a person or private repo. No item is in the last class. Git commit hashes of a private repo count as a finding to report, not a FAIL.
- `images-clean`: open each `preview.png`. Quote any name on screen. There are none.
- `records-true`: compare `BRIEF.md` with its source. Every line in the public copy says what the source says, apart from the anonymized names. Quote any difference.
- `parts-real`: for each part, name the element in the source deck that it comes from. A part with no source is a FAIL.

## Gotchas

- Every file is already on a public branch. A hit means a history rewrite, not a new commit: tell the owner first, and do not force-push on your own.
- The protected list is hashes in `tools/check_cases.py`. To add a name, append its `digest()` value. Do not put the name in a tracked file.
