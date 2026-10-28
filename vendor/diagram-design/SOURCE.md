# Source

These files are copied from diagram-design by Cathryn Lavery, under the MIT
License in `LICENSE` beside this note. `SKILL.md` is the only edited file.
Every other file is byte-identical to upstream.

- Upstream: https://github.com/cathrynlavery/diagram-design
- Version: 2.6.120, commit 0b9b10cab3dbf695642fa1a6c4b4f60df9083689
  (plugin install of 2026-10-25, copied 2026-10-26)
- From `skills/diagram-design/`:
  - `references/`: `type-sequence.md`, `type-flowchart.md`, `type-bar.md`,
    `type-layers.md`, `type-state.md`, `type-timeline.md`, `type-tree.md`,
    `output-spec.md`, `layout-budget.md`, `style-guide.md`,
    `primitives-core.md`, `primitive-annotation.md`, `semantic-patterns.md`,
    `type-architecture.md`
  - `assets/`: `example-<type>-dark.html` for sequence, flowchart, bar,
    layers, state, timeline, and tree
  - `scripts/self_check.py`
- From the repository root: `LICENSE`, `scripts/verify-geometry.py`
- Edited: `SKILL.md`. The routing tables keep only the bundled types,
  pointers to files that are not here are removed, and the section
  "Slide-scale overrides (jungle-deck)" replaces the style-guide gate.

`type-architecture.md` is here only for two sections that
`primitives-core.md` relies on: Connector style (the elbow path) and Crossing
arrows (bridge/hop). `semantic-patterns.md` is here because `type-state.md`
and `type-tree.md` route to it.

The references write `<repo-root>/scripts/verify-geometry.py`. Here it is
`scripts/verify-geometry.py`. Use it on one file, never with `--all`.

`scripts/self_check.py` reads `assets/template-motion.html` only when the
checked file contains a `<script>`. The Verify step checks a script-free
extract, so that template is not bundled.

To update, copy the same files from a newer upstream version, re-apply the
`SKILL.md` edits, and change the version above.

## Not bundled

The bundled files link to these upstream files. They are out of scope for a
jungle-deck figure. An agent skips these links.

- Other types: `type-gantt.md`, `type-line.md`, `type-treemap.md`, and every
  type not in the list above
- Other examples: `example-sequence.html`, `example-sequence-full.html`,
  `example-sequence-oauth.html`, `example-sequence-oauth-dark.html`,
  `example-sequence-oauth-full.html`, `example-flowchart.html`,
  `example-flowchart-full.html`, `example-bar.html`, `example-bar-full.html`,
  `example-layers.html`, `example-layers-full.html`, `example-state.html`,
  `example-state-full.html`, `example-state-lifecycle.html`,
  `example-state-lifecycle-dark.html`, `example-state-lifecycle-full.html`,
  `example-timeline.html`, `example-timeline-full.html`, `example-tree.html`,
  `example-tree-full.html`, `example-architecture.html`,
  `example-architecture-dark.html`, `example-architecture-full.html`,
  `example-architecture-containment.html`,
  `example-architecture-containment-dark.html`,
  `example-architecture-containment-full.html`, `example-data-flow.html`,
  `example-data-flow-dark.html`, `example-data-flow-full.html`,
  `example-nested.html`, `example-nested-dark.html`,
  `example-nested-full.html`, `example-process.html`,
  `example-process-dark.html`, `example-process-full.html`,
  `example-treemap.html`, `example-treemap-dark.html`,
  `example-treemap-full.html`, `example-quadrant-consultant.html`,
  `example-paved-road-animated.html`, `example-queue-animated.html`,
  `icons.html`, `template-motion.html`, and the other templates
- Replaced by the slide-scale overrides: `onboarding.md`, `profiles.md`,
  `animation.md`, `primitive-terminal.md`
- Export: `export.md`, `export-registry.md`
- Repository-only checks: `lint-render.py`, `verify-contrast.py`,
  `verify-docs-sync.py`, `verify-treemap.py`, `verify-dumbbell.py`,
  `test-verify-dumbbell.py`, `verify-architecture-containment.py`
