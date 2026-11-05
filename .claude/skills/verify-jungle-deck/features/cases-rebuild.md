# A case rebuilds its impression on a new topic

A `DESIGN.md` is worth keeping only if an agent that never saw the source deck can use it. This feature proves that for one case per run.

## Sub-features

- `build-from-case`: the real path, from a case pick to a built page.
- `show-proposal`: after the pick, the skill proposes new `Show` lines once. The student's story stays.
- `show-declined`: a student who declines keeps every `Show` line.
- `parts-used`: the page draws with parts that the case names.
- `tokens-only`: the figures use `var(--...)`, so a changed accent reaches them.
- `fits`: `scripts/check_layout.py` passes.
- `impression`: a human compares the page with `preview.png`.

## How to get to it (user POV)

- The student picks a case in `design`, as in `cases-on-request`, and goes on to `build`.

## Driving it with jdv.py

Persona card: the `clear-plan` card (the stack-growth bug in the fixture), plus "<case>로 할게요." at the design question. The topic must differ from the case's own topic, and the fixture's topic does. Stop when `phase` is `revise`. Turn cap 30. Run `jdv.py clean <run>` after. Run one case per run. Do not run two at once: they share the user's hooks and rate limits.

Cheaper path for a change in `design` or `build`: `stage`, then `seed <run> <finished run>`, then `turn <run> "/jdv:jungle-deck jungle-deck 이어서" --new`, and say "<case>로 할게요." The grill does not change, so it does not need to run. Run the two `show-*` predicates first, and stop there while the rule still changes. Go on to `revise` once per case.

Pass predicates:

- `show-proposal`: one message holds a table of current and new `Show` lines (quote it). Each new line names a row of the "Slides" table or a part. Compared with the BRIEF before the pick: every `Thesis`, `Role`, the slide count, the order, and the `Evidence list` have an empty diff. Only the lines the student took changed.
- `show-declined`: in a separate run, the student answers "아니요, 그대로 둘게요". The `Slide theses` table has an empty diff. Stop at the next question.
- `build-from-case`: `BRIEF.md` § Design has `Source: cases/<case>/DESIGN.md`, and the transcript has a read of that file before the first write of the page.
- `parts-used`: at least two class names from the case's "Slides" table, "CSS to add", or "Figure vocabulary" snippets appear in a `<section>`, beyond `.head`, `.foot`, and `.panel`. Name them. Report which rows and parts of the case did not reach the page, because a pass can still miss the case's signature. A figure on the page that ignores the case's rule (for example, accent on every node) is a FAIL with a quote.
- `tokens-only`: in the page's `<section>` elements, `grep -E '#[0-9a-fA-F]{3,8}\b'` has no hit in an SVG attribute.
- `fits`: run `python3 scripts/check_layout.py <page>` yourself. Exit 0. Record the note if web fonts did not load.
- `impression`: save one screenshot per figure slide to `<scratch>/evidence/<feature>-<case>/`, and hand them to the user with `cases/<case>/preview.png`. No predicate decides this.

## Gotchas

- Measured 2026-11-05 before `Show lines from a case` (issue #42): `parts-used` failed. The page had no `.frames`, no `.two`, and no `.lit`.
- Measured 2026-11-05 after it, seeded from a finished run (6 slides, 5 student turns per run, every `show-*`, `tokens-only`, and `fits` passed):
  - `week07-circular-list`: `.two`, `.frames`, `.lit`, `.three`, `.col`, `.punch`. None of the six named figure parts fit the topic. Slide 06 wraps badly around a `.punch` square.
  - `week09-clean-code`: `.thesis-row`, `.closing`, `IDE panel`, `Read line`, `Name marker`. `Wall`, `Fold`, `Tree`, and `Table` did not reach the page, because the fixture's evidence holds one code line. So this fixture cannot prove that case's signature. It needs a topic with a long function.
- Measured 2026-11-04 with a subagent, not with this path: one rebuild took 17 minutes and 131,000 tokens. Budget for it, and pick the case that the user cares about first.
- `week04-array-in-c`, `week05-oop-in-c`, `week06-bsize-cast`, and `week08-p2-team-workflow` have had no full rebuild. Report them as unverified until they run.
- The first `parts-used` wording named only "Figure vocabulary" snippets. Many of those parts are SVG recipes with no class, and a page cannot match them by class. The verdicts above use the current wording.
- Headless Chrome can stall on Google Fonts in WSL. `--headless` with `--virtual-time-budget` works where `--headless=new` hangs. Remove the font `<link>` and load a local copy for a screenshot; do not change the page.
- A failure here means the `DESIGN.md` or `reference/build.md` must change. Do not weaken a predicate.
