# Figures show one point and stay legible

Build draws a figure for each slide whose `Show` line has a shape. Each figure
shows only what its `Show` line names, reads at slide size, and reveals in steps.

## Sub-features

- `show-recorded`: grill writes a `Show` line for every slide thesis, with no extra question.
- `figure-drawn`: a slide whose `Show` line names an order, a branch, a path, a layout, or a quantity has a figure (HTML boxes or one inline `<svg>`) with `data-step`.
- `one-point`: each figure holds 6 or fewer nodes, rows, or bars, and 4 or fewer steps.
- `legible`: `scripts/check_layout.py` reports no `small text`.
- `guide-read`: build opens `vendor/diagram-design/SKILL.md` before the first figure.

## How to get to it (user POV)

- Continue the `clear-plan` persona through design and build, as in `slides-match-intent`.

## Driving it with jdv.py

Persona card: the `clear-plan` card. At the theses round, accept the drafted `Show` lines.

Steps: as in `slides-match-intent.md`. Stop when `phase` is `revise`. Run `jdv.py clean <run>`.

Pass predicates:

- `show-recorded`: every `Slide theses` row of `BRIEF.md` has a non-`TBD` `Show` cell. The grill turn count is the same as in a `clear-plan` run at the previous revision, or lower.
- `figure-drawn`: count the slides whose `Show` cell names a shape. Each one holds an inline `<svg>` or a `.box` group, and at least one `[data-step]` inside it. Quote one `Show` cell and its figure's text.
- `one-point`: for each figure, count the text-bearing nodes, rows, or bars, and the distinct `data-step` values. All within the budget.
- `legible`: run `scripts/check_layout.py <page>` yourself. No line has `small text`.
- `guide-read`: the build transcript has a read of `vendor/diagram-design/SKILL.md` before the first write of an `<svg>`.

## Gotchas

- The user judges whether a figure looks good; no predicate does. Hand the page to the user.
- Build starts the revise server; always run `jdv.py clean` after.
