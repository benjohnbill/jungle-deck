---
name: diagram-design
description: Partial copy of diagram-design 2.6 vendored for jungle-deck. Draws a flowchart, sequence, state machine, timeline, tree, layer stack, or bar chart as inline SVG in one slot of a jungle-deck slide, under slide-scale overrides.
license: MIT
metadata:
  version: "2.6"
---

# Diagram Design

Create diagrams as inline SVG with an editorial design system.

This partial copy ships seven of the forty-five upstream visual types. Semantic patterns describe behavior; type references describe layout. A bundled reference may link to an upstream file that is not here: another type, a light or full example, a template, onboarding, profiles, animation, export, import, icons, or a repository-only script. Skip that link. [SOURCE.md](SOURCE.md) lists what was taken and what was left out.

---

## Slide-scale overrides (jungle-deck)

You draw one figure into one slot of a jungle-deck slide. Where this section and any other rule in this copy disagree, this section wins. It replaces:

- The style-guide gate, client profiles, and onboarding. Ask no setup questions.
- The hex values and font families in §5, §9, `references/style-guide.md`, and the examples.
- The type ramp and the `min-width` scroll wrapper in `references/output-spec.md`.
- The single-file output in §12, and the motion layer.

Work unattended. Decide the type, the size, and the cuts yourself, and list them in your final report.

**Select before you draw.** The talk is 2 minutes, so a figure shows one point, not a whole mechanism. Your input is the slide's row in `BRIEF.md`: the thesis, the `Show` line, and the slide's script or notes.

- Draw only what the `Show` line names. When the row has no `Show` line, draw only what the thesis and the script name.
- Leave out the rest of the mechanism, even when the context or the source code holds it. When the audience needs one neighbour to place the point, keep it as a dimmed node in `var(--mut)` with no accent and no step of its own.
- Put the accent on the path the speaker talks through, and only there.
- Hold the budget: 6 or fewer nodes, rows, or bars, and 4 or fewer `data-step` groups. When the `Show` line needs more, the slide holds two points: split it into two slides and report the split. Do not shrink type to fit more.
- In your final report, list what you left out.

**Output.** Write one inline `<svg>` inside the slot element. Change nothing outside the slot. Style the SVG `width:100%; max-height:70vh; display:block`. Use presentation attributes, because a `<style>` inside an inline SVG applies to the whole deck. Prefix every `id` in the SVG with the slot id (`<slot>-title`, `<slot>-desc`, `<slot>-arrow`). A deck holds several figures, and a repeated id resolves to the first one.

**Tokens.** Take every color and font from the deck's `:root`. Write them as `var(--…)` or `color-mix()` in `fill`, `stroke`, and `font-family` attributes. Both forms resolve in SVG attributes in Chrome 156 and Firefox 156 (measured on stage.html).

| diagram-design role | Deck value |
|---|---|
| `paper` | `var(--paper)` |
| `ink`, `ink-strong` | `var(--ink)` |
| `muted`, `soft`, `link`, `series-*` | `var(--mut)` |
| `accent` | `var(--acc)`, the only hue |
| Node fills, `paper-2`, frame and band washes | `color-mix(in srgb, var(--ink) 12%, var(--paper))` |
| `accent-tint` (focal fill) | `color-mix(in srgb, var(--acc) 18%, var(--paper))` |
| `rule`, `rule-solid`, gridlines | `var(--grid)`, decoration only |
| `node-name`, `title`, `callout` | `var(--font-body)` |
| `sublabel`, `arrow-label`, `eyebrow` | `var(--font-mono)` for identifiers and values, `var(--font-body)` for Korean and prose |

A translucent role such as `{ink @ 0.20}` becomes `var(--mut)` on a line that carries meaning and the node-fill mix on a fill. `var(--panel)` is a node fill only when it passes the fill minimum below.

**Contrast and visibility first.** The examples use 0.8–1px hairlines, 2–6% washes, and 7–9px labels, which read flat on a projector. Hold these minimums. Measure them with the WCAG 2 formula against the deck's real `:root` hex values, and resolve a `color-mix()` fill before you measure.

- Text: 4.5:1 against the fill it sits on. 3:1 is enough only at 24px, or at 18.7px with weight 600 and up.
- Lines that carry meaning (node border, connector, lifeline, axis, divider, bracket): a solid deck color at 3:1 against its background, with no `opacity`. Stroke width 2 for node borders and connectors, 1.5 for lifelines and dividers (dashes allowed), and 3 for the focal node and the headline path.
- Node fill: 1.25:1 against the slot background. `var(--panel)` on `var(--paper)` measures 1.06–1.09:1 on the stage.html placeholder and on a dark deck. The 12% ink mix measures 1.30–1.32:1 on both.
- `var(--grid)` and any fill under 1.25:1 are decoration. Carry meaning with a labeled shape or a line.

**Type at slide scale.** At 1280×720 a full-width slot under a slide heading is about 1180 × 440 px. (In stage.html with the style above, a `0 0 1160 440` viewBox rendered at s = 1.01 in Chrome 156 and Firefox 156.) Rendered px = font-size × s, where s = min(slot width ÷ viewBox width, slot height ÷ viewBox height). Make the viewBox no larger than the slot, about `0 0 1160 440` for a full-width slot and `0 0 560 440` for a half-width one. Then s ≥ 1, and N units render at N px or more. The same holds for the stroke widths above. Minimum font-size in viewBox units:

- 16 for node names.
- 14 for every other label: conditions, arrow labels, sublabels, values, and group names.
- 12 for ticks, tags, and eyebrows. Nothing goes below 12.

Make each label mask 4 taller than its text and as wide as the `style-guide.md` width budget. When text does not fit, cut words or split the figure, and keep the size.

**Nodes state the mechanism and its condition.** The figure is judged on this first. Name the concrete thing in each node: the function, field, register, or value that acts or holds state (`sys_write()`, `f->R.rax`, `rsp = USER_STACK`). Label each branch and transition with the real condition that selects it (`fd == 1`, `!is_user_vaddr(buf)`). Take these words from the slide's notes, and add only detail the notes carry. Identifiers keep their case and use `var(--font-mono)`. The 14-character, all-caps limit for arrow labels (§6 rule 2) applies to plain words only. The mask and its 6–10px gap apply to every label.

**Legend only for an unstated encoding.** When every node and line is named on the figure, or the type's own grammar carries the meaning (flowchart shapes, sequence lifelines), the figure is self-evident. Then the labels are the legend: skip the legend strip, the legend items in §9, and the 60px legend allowance.

**Name groups with brackets.** When several nodes form a group the speaker names ("남은 일", "파일 계열"), draw a square bracket or a curly brace outside the group and put the group name beside it. Draw it as a `<path>` in `var(--mut)`, or in `var(--acc)` when the group is the focus, at stroke 2, with the name at 14 or more. A bracket is meta pointing, not an annotation callout, so the 2-callout budget does not count it. Reach for a bracket before an extra container node or a legend.

**Separate dense text.** Give every block of text air. Use the presentation column of `references/output-spec.md` §2: node box height 64 or more and 40 or more between nodes. Space rows, messages, and list lines at least 2.5× their label size apart (36 at 14px labels, where upstream allows 24). Set two-line labels at a line pitch of 1.3× the font size. Separate groups with a band (a node-fill rect behind the group) or with 40 units of empty space.

**Step reveal.** Put each story beat in `<g data-step="N">`, numbered 1, 2, … in the order of the slide's notes (`▸N`). Context the audience needs from the start (actors, lifelines, axes, the frame) carries no `data-step`. stage.html reveals any `[data-step]` element, SVG groups included (measured with the real stage.html in Chrome 156 and Firefox 156). Put a needed `transform` on a nested `<g>` inside the step group. The stage's CSS `transform` replaces a `transform` attribute on the `<g data-step>` itself, and the group snaps to the origin. A connector and its label join the step of the node they reach. Use 4 steps or fewer ("Select before you draw").

**Flowchart on a slide.**
- Start at an entry pill named with the real function (`syscall_handler(f)`). Put the first decision directly after it.
- Draw a multi-way branch as a bus: one trunk leaves the decision, and each case leaves the trunk on its own row toward its node.
- Label every exit with a chip: a rect 24 high, `rx` 4, in the node-fill mix, mono text 14 or more at weight 600 (`SYS_WRITE`, `fd == 1`, `예`, `아니오`). Place it beside its line, 8 off.
- End every path in a named end node (`반환값 기록 · f->R.rax`, `exit(-1)`).
- Use orthogonal routes: straight runs and right-angle elbows.

**Progress or done-of-total bars.** The audience must see where work remains and how much.
- Draw the done part as a solid fill at 3:1 or more against the paper. A dark gray near the paper color washes out on a projector.
- Draw the remaining part hatched: an SVG `<pattern>` of diagonal lines in `var(--mut)`, with a 2 outline. On the rows the speaker names as remaining work, draw the hatching and the outline in `var(--acc)`.
- Write the remaining count inside the remaining part when it fits (`5개 남음`), mono 14 or more. Write `done / total` at the bar end.
- Group rows by status with brackets in the right margin, named by state: `다 끝남`, `진행 중`, `남은 일`.

**Verify.** Copy the slot's `<svg>…</svg>` alone into a temporary `.html` file next to the deck. Run `python3 <this folder>/scripts/self_check.py <tmp>` and `python3 <this folder>/scripts/verify-geometry.py <tmp>`. Both must pass. Then delete the temporary file. Run them on the extract only: on the whole deck, `scripts/self_check.py` fails by design, because the stage runtime is a `<script>`.

---

## 1. Philosophy

**The highest-quality move is usually deletion.**

Applied to schematics:

- Every node represents a distinct idea. Two nodes that always travel together are one node.
- Every connection carries information. If the relationship is obvious from layout, remove the line.
- Coral is **editorial, not a flag.** 1–2 focal nodes per diagram. Using it on 5 nodes erases the signal.
- The schematic isn't done when everything is added. It's done when nothing can be removed.

**Target density: 4/10.** Enough to be technically complete. Not so dense it needs a guide. Above 9 nodes, it's probably two diagrams.

---

## 2. When to Use

Use for any of the seven bundled visual types (§3) when a reader will learn more from a visual than from prose, a table, or a bulleted list.

**Don't use for:**

- Quick unicode diagrams → a separate plain-text tool such as wiretext. This skill doesn't ship one.
- Lists of things → table or bullets.
- Attribute-only before/after → table.
- One-shape "diagrams" → just write the sentence.

Before drawing, ask: *Would the reader learn more from this than from a well-written paragraph?* If no, don't draw.

---

## 3. Selection: semantic pattern, then visual type

When behavior, state, enforcement, or risk carries the meaning, first load [`references/semantic-patterns.md`](references/semantic-patterns.md) and choose one primary pattern. Then choose the nearest visual type for layout. If no pattern matches, choose the type directly.

| Behavioral trigger | Semantic pattern → nearest type |
|---|---|
| Two rule traces need pass/fail/skipped/not-reached and first divergence | **Paired policy-evaluation traces** → Flowchart |
| Controls grouped by where they are enforced | **Governance / control catalog** → Layer stack |
| Defenses compensate for prior gaps and residual risk propagates | **Compensating security layers** → Layer stack |
| Hierarchical, ID-addressable decomposition needing per-block I/O, constraints, and a code link | **Traceable block decomposition** → Tree |
| One subject progresses through phases, waits, retries, cancellation, and terminal outcomes | **Lifecycle phase map** → State Machine |

The pattern owns semantic primitives and its tighter budget; the type owns layout grammar. Step reveal follows the slide-scale overrides.

### Visual-type guide (7 bundled)

| If you're showing… | Use | Reference |
|---|---|---|
| Decision logic with branches | **Flowchart** | [type-flowchart.md](references/type-flowchart.md) |
| Time-ordered messages between actors | **Sequence** | [type-sequence.md](references/type-sequence.md) |
| States + transitions + guards | **State machine** | [type-state.md](references/type-state.md) |
| Events positioned in time | **Timeline** | [type-timeline.md](references/type-timeline.md) |
| Parent → children relationships | **Tree** | [type-tree.md](references/type-tree.md) |
| Stacked abstraction levels | **Layer stack** | [type-layers.md](references/type-layers.md) |
| Quantitative comparison across categories | **Bar chart** | [type-bar.md](references/type-bar.md) |

Rules of thumb:

- If a 3-column table communicates the same thing, pick the table.
- If two types seem useful, pick the dominant axis; a semantic pattern may add behavior-specific primitives, not a second layout grammar.
- If you're past the complexity budget (§7), split into an overview + detail.

**Always load the chosen type reference linked in the guide before drawing.** When routed above, also load `semantic-patterns.md`.

### Confirm before drawing

Before rendering, state the plan in one short message: the chosen visual type (and semantic pattern, if routed), the size preset, and anything the complexity budget (§7) will force out. If the user is reachable, let them redirect before you draw; if not, proceed and note the assumptions beside the deliverable. Skip the pause only when the request already pins type, size, and content exactly.

---

## 4. Universal Anti-patterns

These mark "AI slop" schematics of any type:

| Anti-pattern | Why it fails |
|---|---|
| Dark mode + cyan/purple glow | Looks "technical" without design decisions |
| JetBrains Mono as blanket "dev" font | Mono is for *technical* content — ports, commands, URLs. Names go in Geist sans. |
| Identical boxes for every node | Erases hierarchy |
| Legend floating inside the diagram area | Collides with nodes |
| Arrow labels with no masking rect | Bleeds through the line |
| Vertical `writing-mode` text on arrows | Unreadable |
| 3 equal-width summary cards as default | Generic grid — vary widths |
| Shadow on any element | Shadows are out. Borders are in. |
| `rounded-2xl` on boxes | Max radius 6–10px or none |
| Coral on every "important" node | Coral is 1–2 editorial accents, not a signaling system |
| Reproducing Mermaid's renderer layout | Imports automatic spacing and routing instead of making an editorial layout |
| Any breach of the six §6 connector rules | Automatic fail: diagonal slants, labels touching their stroke, masks clipped by a later node, overlapping paths, shared attach points, transit behind a non-endpoint box |

Type-specific anti-patterns live in each type reference linked in the guide.

---

## 5. Design System

**The design system is skinnable.** [`references/style-guide.md`](references/style-guide.md) is the single source of truth for colors, typography, tokens, and the default palette; this file names semantic roles (`paper`, `ink`, `muted`, `accent`, `link`, …). In this copy the deck is the brand: the slide-scale overrides map each role to a deck token.

> When specs below or in type references mention "ink", "accent", "muted", etc., use the deck token from the slide-scale overrides.

Type-reference snippets write roles as placeholders: `{ink}`, `{ink @ 0.40}` for a role at an opacity, and `{node-name}`, `{sublabel}`, `{eyebrow}`, `{arrow-label}`, `{title}`, `{callout}` for fonts. Resolve every placeholder against the slide-scale overrides before emitting.

### Semantic roles (at a glance)

| Role | Purpose |
|---|---|
| `paper`, `paper-2` | Page bg and container bg |
| `ink` | Primary text / stroke |
| `muted`, `soft` | Secondary text, default arrows, sublabels |
| `rule`, `rule-solid` | Hairline borders |
| `accent`, `accent-tint` | 1–2 focal elements per diagram |
| `link` | HTTP/API calls, external arrows |

**Focal rule:** `accent` goes on 1–2 elements max. Everything else is `ink` / `muted` / `soft`. If you're tempted to accent 4 things, you haven't decided what's focal yet.

**Node treatments** (focal, backend/API/step, store/state, external/cloud, input/user, optional/async, security/boundary): fill and stroke per [style-guide.md § Node type → treatment](references/style-guide.md#node-type--treatment).

**Typography:** Instrument Serif for the H1 title and italic callouts, Geist sans 600 for node names, Geist Mono for sublabels, eyebrows, and arrow labels. Sizes, weights, and the font `<link>`: [style-guide.md § Typography](references/style-guide.md#typography); per-preset type ramp: [output-spec.md](references/output-spec.md). When the user asks for offline output, system fonts, or no Google Fonts, follow [style-guide.md § Font source](references/style-guide.md#font-source).

**Non-Latin labels** — extend the family: [Korean](references/style-guide.md#korean-labels), [Chinese](references/style-guide.md#traditional-chinese-labels), [Cyrillic](references/style-guide.md#cyrillic-labels).

**Mono is for technical content only** — never as a blanket "dev" font, and never JetBrains Mono.

---

## 6. Core SVG Primitives

Universal building blocks. Type-specialized primitives (lifeline, activation bar, region) live in the relevant type reference linked in the guide. Optional primitive:

- Editorial callouts → [primitive-annotation.md](references/primitive-annotation.md)

Exact markup (background, dotted paper, markers, node box, arrow label, legend) and the long form of each connector rule: [`references/primitives-core.md`](references/primitives-core.md). The elbow-path formula and the bridge/hop at a crossing live in [`references/type-architecture.md`](references/type-architecture.md) § Connector style and § Crossing arrows. That file is bundled for those two sections only.

- **Arrows:** `muted` by default, `accent` for the headline path, `link` for HTTP/API and external calls, dashed `5,4` for optional, passive, return, or async. Draw arrows before boxes so lines sit behind nodes.
- **Node box:** an opaque paper mask rect, then the styled box at `rx=6`, a rectangular type tag at `rx=2` (not a pill), the name in Geist 600, and a Geist Mono sublabel.

### Mandatory connector rules

Non-negotiable, and §9 checks each one. Full text and edge cases: [primitives-core.md § Mandatory connector rules](references/primitives-core.md#mandatory-connector-rules).

1. **Orthogonal only.** Connectors between off-axis nodes are rounded right-angle elbows at `r=8` (`r=6` minimum in tight layouts); a straight `<line>` only when both ends share x or y. Diagonals fail.
2. **Label gap.** Every arrow label (14 characters max, all caps, centered on its segment) sits on an opaque mask with a visible 6 to 10px gap from its stroke, beside vertical segments, never on the line.
3. **No overlaps.** No shared or stacked strokes: offset parallel routes by 12px or more, and use the bridge/hop at a single crossing.
4. **Fan attach points.** Connectors on one box edge each get their own point at `L * k / (N + 1)`, 12px or more apart (8px on very small boxes).
5. **No transit behind a non-endpoint box.** Reroute. Only when the box is geometrically unavoidable: dashed stroke (`4,3`), label at the visible end, no marker on the intervening box.
6. **Mask before node.** A label mask must not overlap a node drawn after it; badge masks fully inside a node and masks over earlier zones are fine. Verify with `python3 scripts/verify-geometry.py <file>` from this folder.

---

## 7. Layout & Spacing

Structural geometry sits on a 4px grid: node origins, widths, heights, gaps, and padding divide by 4. Type sizes follow the role ramp in [output-spec.md](references/output-spec.md), not the grid. Allowed values, the off-grid exceptions, and page layout: [`references/layout-budget.md`](references/layout-budget.md).

### Complexity budget (per diagram)

| Limit | Rule |
|---|---|
| Max nodes | 9 |
| Max arrows / transitions | 12 |
| Max coral elements | 2 |
| Max annotation callouts | 2 |
| Max reveal steps | 8 (step reveal per the slide-scale overrides) |

Per-type limits (lifelines, lanes, series, bars, stages, and the rest): [layout-budget.md § Complexity budget](references/layout-budget.md#complexity-budget-per-diagram). Check your type's row before drawing.

If you exceed, split into two diagrams (overview + detail).

---

## 8. Summary Card Pattern

Don't use 3 identical generic cards. Vary the treatment: column widths such as `1.1fr 1fr 0.9fr`, a white background with a 1px hairline border and 6px radius, no `box-shadow`. Markup and the card-dot variants: [layout-budget.md § Summary Card Pattern](references/layout-budget.md#summary-card-pattern).

---

## 9. Pre-Output Checklist (Taste Gate)

Run before producing any diagram.

**Type fit:**

- [ ] If behavior matters, did I choose one semantic pattern before the visual type and load `semantic-patterns.md`?
- [ ] Right visual type for the layout? (§3 visual-type guide)
- [ ] Stated type, pattern, size preset, and planned cuts before drawing — confirmed, or assumptions noted? (§3)
- [ ] Would a table / paragraph do the same job? (If yes — don't draw.)
- [ ] Loaded the matching type reference linked in the visual-type guide?

**Remove test:**

- [ ] Can I remove any node? (Would a reader still understand?)
- [ ] Can I merge any two nodes? (Do they always travel together?)
- [ ] Can I remove any arrow? (Is the relationship obvious from layout?)
- [ ] Can I remove any label? (Does color or shape already signal it?)

**Signal:**

- [ ] Coral used on ≤2 elements? If more, which actually deserve focal status?
- [ ] Legend covers every type used — and nothing extra?
- [ ] Within the type's complexity budget (§7)?

**Technical:**

- [ ] Diagram `<svg>` has `role="img"` and `aria-labelledby` resolving to its `<title>` and `<desc>`?
- [ ] `<title>` is the first child of `<svg>` (before `<defs>`) and both `<title>` and `<desc>` are filled in?
- [ ] `<title>` / `<desc>` IDs are prefixed for this diagram and variant — never bare `title` / `desc`?
- [ ] Arrows drawn before boxes?
- [ ] **§6 rule 1:** off-axis connectors are `r=8` elbows, no diagonal slants?
- [ ] **§6 rule 2:** a visible 6 to 10px gap between every label mask and its connector?
- [ ] **§6 rule 3:** no overlapping or stacked connectors; bridge/hop at crossings?
- [ ] **§6 rule 4:** a distinct attach point per connector on a shared edge, 12px or more apart, none hiding another?
- [ ] **§6 rule 5:** no transit behind a non-endpoint box, except the unavoidable case (dashed, label at the visible end)?
- [ ] **§6 rule 6:** no label mask overlapping a node drawn after it? (Run `python3 scripts/verify-geometry.py <file>` from this folder.)
- [ ] Every arrow label has an opaque `{paper}` rect behind it?
- [ ] Legend is a horizontal bottom strip, not floating?
- [ ] No vertical `writing-mode` text?
- [ ] `viewBox` expanded for the legend strip (~60px)?
- [ ] SVG sized per the slide-scale overrides (`width:100%; max-height:70vh`), with no `min-width` and no scroll wrapper?
- [ ] Node origins, dimensions, gaps, padding on the 4px grid; type sizes on the role ramp?
- [ ] From the installed skill directory, did `python3 scripts/self_check.py <file>` pass? (Accessible-SVG contract, single-file safety, content inside the viewBox, motion basics.)
- [ ] Step reveal per the slide-scale overrides: each beat in a `<g data-step>` in the notes' order, with no `transform` attribute on the stepped group itself?

**Typography:**

- [ ] Brand match uses exact public families/weights, verified via `getComputedStyle`; fallbacks disclosed?
- [ ] Human-readable names in Geist sans, not Geist Mono?
- [ ] Technical sublabels (ports, commands, URLs) in Geist Mono?
- [ ] Page title in Instrument Serif?
- [ ] Annotation callouts (if any) in *italic* Instrument Serif? (see [primitive-annotation.md](references/primitive-annotation.md))
- [ ] No JetBrains Mono anywhere?

---

## 10. Examples

This copy ships one example per bundled type, the minimal dark variant: `assets/example-<type>-dark.html` for `sequence`, `flowchart`, `bar`, `layers`, `state`, `timeline`, and `tree`. Read the one for your type for markup. The slide-scale overrides replace its hex colors, fonts, `min-width`, and 7–9px type.

### To create a new diagram

1. If behavior is load-bearing, choose a semantic pattern; then load the matching type reference linked in the visual-type guide.
2. Read that type's dark example for markup.
3. Write the `<svg>` into the slot per the slide-scale overrides, and fill `<title>` / `<desc>`.
4. Run the §9 taste gate and the Verify step of the slide-scale overrides.

---

## 11. Importing

Not bundled in this copy.

---

## 12. Output

Always produce a single self-contained `.html` file:

- Embedded CSS (no external except Google Fonts)
- Inline SVG (no external images)
- Static by default; minimal inline JavaScript only for explicit animation controls/state

Renders correctly in any modern browser. Motion-enabled output must render its complete meaning without JavaScript; under `prefers-reduced-motion: reduce` it shows the complete static frame and hides/disables playback controls.

### Accessible SVG contract

Every diagram is an accessible figure by default (long form: [primitives-core.md § Accessible SVG contract](references/primitives-core.md#accessible-svg-contract)):

1. `<svg>` carries `role="img"` and `aria-labelledby` naming its `<title>` and `<desc>`.
2. `<title>` is the first child of `<svg>`, before `<defs>`.
3. IDs are `<slug>-title` / `<slug>-desc`, the slug matching the file (`loop`, `loop-dark`, `loop-full`); never bare `title` / `desc`.
4. `<title>` is the subject's short name, roughly the page `<h1>`, 60 characters or fewer.
5. `<desc>` is one sentence about the content, not the geometry.
6. Decorative-only SVG carries `aria-hidden="true"` instead.

### Exporting to PNG / SVG

Not bundled in this copy. The figure lives inline in the deck.
