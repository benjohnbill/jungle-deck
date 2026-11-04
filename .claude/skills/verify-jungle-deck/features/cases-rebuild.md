# A case rebuilds its impression on a new topic

A `DESIGN.md` is worth keeping only if an agent that never saw the source deck can use it. This feature proves that for one case per run.

## Sub-features

- `build-from-case`: the real path, from a case pick to a built page.
- `parts-used`: the page draws with parts that the case names.
- `tokens-only`: the figures use `var(--...)`, so a changed accent reaches them.
- `fits`: `scripts/check_layout.py` passes.
- `impression`: a human compares the page with `preview.png`.

## How to get to it (user POV)

- The student picks a case in `design`, as in `cases-on-request`, and goes on to `build`.

## Driving it with jdv.py

Persona card: the `clear-plan` card (the stack-growth bug in the fixture), plus "<case>로 할게요." at the design question. The topic must differ from the case's own topic, and the fixture's topic does. Stop when `phase` is `revise`. Turn cap 30. Run `jdv.py clean <run>` after. Run one case per run. Do not run two at once: they share the user's hooks and rate limits.

Pass predicates:

- `build-from-case`: `BRIEF.md` § Design has `Source: cases/<case>/DESIGN.md`, and the transcript has a read of that file before the first write of the page.
- `parts-used`: at least two class names from the case's "Figure vocabulary" snippets appear in the page. Name them. A figure on the page that ignores the case's rule (for example, accent on every node) is a FAIL with a quote.
- `tokens-only`: in the page's `<section>` elements, `grep -E '#[0-9a-fA-F]{3,8}\b'` has no hit in an SVG attribute.
- `fits`: run `python3 scripts/check_layout.py <page>` yourself. Exit 0. Record the note if web fonts did not load.
- `impression`: save one screenshot per figure slide to `<scratch>/evidence/<feature>-<case>/`, and hand them to the user with `cases/<case>/preview.png`. No predicate decides this.

## Gotchas

- Measured 2026-11-05 (`week07-circular-list` base, `Branch graph` from week08, 21 student turns): `tokens-only` and `fits` passed, and the base look and the accent rule came through. `parts-used` failed for scenes: the page has no `.frames`, no `.two`, and no `.lit`. Grill fixes the `Show` lines before the case pick, and build draws only what `Show` names, so a case's composition cannot reach the page. Do not weaken this predicate: the fix belongs in the design phase.
- Measured 2026-11-04 with a subagent, not with this path: one rebuild took 17 minutes and 131,000 tokens. Budget for it, and pick the case that the user cares about first.
- Only `week07-circular-list` has had a rebuild, and that was its first draft. Report the others as unverified until they run.
- Headless Chrome can stall on Google Fonts in WSL. `--headless` with `--virtual-time-budget` works where `--headless=new` hangs. Remove the font `<link>` and load a local copy for a screenshot; do not change the page.
- A failure here means the `DESIGN.md` or `reference/build.md` must change. Do not weaken a predicate.
