# Build ignores the installed frontend-slides skill

Decided 2026-11-09 by the author, after the frontend-slides plugin moved
from 1.0.0 to 2.1.0. SPEC D15, D17.

## Context

D15 said: use the `frontend-slides` skill when it is installed, in both
`design` and `build`. Version 2.x makes a fixed 1920×1080 stage
non-negotiable: one canvas, scaled as a whole with `transform`. The build
contract in `reference/build.md` is the 1.0 viewport model in
`templates/stage.html`: each slide is one viewport high, sizes use
`clamp()`, and `ViewportContractTest` plus `scripts/check_layout.py` check
it. With 2.x installed, build received two conflicting stage rules. A
student without the skill used only the vendored files and saw no conflict.

## Decision

- `build` never loads the installed `frontend-slides` skill. It follows
  `templates/stage.html` and `vendor/frontend-slides/` only.
- `design` may still read the installed skill's style catalog to propose
  styles. It does not run that skill's question flow or preview files.
- The vendored copy stays at commit `8dca834` (1.0 model).

## Consequences

- Every environment builds through one path, with or without the skill.
- 2.x features (fixed stage, density modes, the Bold Template Pack) are
  not used in build. Adopting the fixed stage needs a rewrite of
  `stage.html`, the layout check, and its tests; that is a separate
  decision.
- The Bold Template Pack (MIT, `zarazhangrui/beautiful-html-templates`)
  uses color keys `bg`, `fg`, `accent`, which the D25 mapping does not
  read. As a design source, its colors are filled by hand.
