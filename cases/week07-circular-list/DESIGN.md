---
version: alpha
name: Circular List
description: Swiss white page, one signal color. A mechanism told in scenes. The accent marks what this scene changed.
colors:
  canvas: "#ffffff"
  ink: "#0a0a0a"
  primary: "#ff3300"
  ink-mute: "#6b6b6b"
  surface: "#f7f7f5"
  hairline: "#ebebeb"
typography:
  display: { fontFamily: IBM Plex Sans KR, fontWeight: 700, letterSpacing: -0.02em, lineHeight: 1.2 }
  body: { fontFamily: IBM Plex Sans KR, fontWeight: 400, lineHeight: 1.5 }
  mono: { fontFamily: IBM Plex Mono, fontWeight: 400, lineHeight: 1.6 }
---

# Circular List

Use this style for a talk that explains how a mechanism works: pointers, memory, a call that changes state.
Build on `templates/stage.html`. Do not change its runtime. Uncomment its IBM Plex `<link>` and font tokens. Map the colors with `reference/design.md` § Token mapping.

All SVG below follows `vendor/diagram-design/SKILL.md` § Slide-scale overrides. Prefix each `id` with the slot id; `SLOT` below is that prefix.

Set the viewBox to the slot. Scene figure: `0 0 760 310`. Compare column: `0 0 400 200`. Full width: `0 0 1160 330`. Coordinates below are examples: keep the font sizes and stroke widths, and re-space the shapes to fit. A row of 4 nodes uses width 150. A row of 6 uses width 110.

## The one rule

**Accent = what this scene changed.** Everything else is ink or muted.

- In a scene, the pointers that this call wrote are accent. Pointers from earlier scenes go back to ink.
- The code line that caused the scene is accent. Only that line.
- A node gets an accent border only when this scene added it.
- A thesis holds one or two `<b>` accent words.
- In a compare slide, the winner column is `.panel.accent`. A loser column has accent only on its problem.

The accent is 3.67:1 on white. In a figure, accent text is weight 600 or more at size 19 or more. For a smaller figure label, use ink.

## Slides

| Slide | Parts |
|---|---|
| Cover | `.tags`, `h1` with one `<em>`, `.rule`, `.sub`, `.dot` |
| Question | `h1` only, one sentence, one `<em>`, no foot |
| Scene | thesis, `.two` (code panel and `.frames`), `.punch` on the last step |
| Compare | thesis, `.three` (three `.col.panel`, one step per column), `.punch` on the last step |
| Timeline | thesis, one wide SVG, `.msgs` (three short notes) |
| Close | the cover `h1` again, `.rule`, `.takeaway`, `.punch` |

Usual order: cover, one attempt that failed, question, compare, scene, close.
The thesis is small (`--h3-size`). The figure is the slide.
`.head`: the section name, or the identifier under discussion, on the left. The number is on the right. `.foot`: the source file or the tool that proves the slide. The cover foot has the talk length on the right.

## CSS to add

Add this to the deck `<style>`. These classes are not in `stage.html`.

```css
h2.thesis { font-size: var(--h3-size); max-width: none; }
:root { --node: color-mix(in srgb, var(--ink) 12%, var(--paper)); }
h2.thesis b { color: var(--acc); }
.sub { color: var(--mut); font-size: clamp(1.1rem, 1.5vw, 2.1rem); line-height: 1.6; max-width: 38ch; }
.tags { display: flex; gap: .7em; }
.eyebrow { font-family: var(--font-mono); font-size: var(--small-size); letter-spacing: .2em; text-transform: uppercase;
           color: var(--paper); background: var(--acc); border: 2px solid var(--acc); padding: .35em .75em; }
.eyebrow.ghost { text-transform: none; letter-spacing: .04em; color: var(--acc); background: var(--paper); }
.dot { position: absolute; right: var(--slide-padding); top: 50%; transform: translateY(-50%);
       width: clamp(36px, 5.5vw, 68px); aspect-ratio: 1; border-radius: 50%; background: var(--acc); }
.two { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.6fr); gap: clamp(.6rem, 1.6vw, 1.4rem); align-items: center; }
.three, .msgs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(.6rem, 1.6vw, 1.4rem); }
.col { display: flex; flex-direction: column; }
.col ul { list-style: none; padding: 0 .7em .7em; font-size: var(--body-size); }
.col li.no::before  { content: "✗ "; color: var(--acc); font-weight: 700; }
.col li.yes::before { content: "✓ "; font-weight: 700; }
.msg { border-top: 2px solid var(--ink); padding-top: .5em; font-size: var(--body-size); }
.msg .k { display: block; font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); }
.takeaway { border: 2px solid var(--ink); padding: 1.2em 1.5em; max-width: 58ch; font-size: var(--body-size); line-height: 1.7; }
.takeaway b { color: var(--acc); }
.takeaway small { color: var(--mut); }
```

## Scenes

A scene slide shows one frame at a time in one place. The figure is one `<svg>`, and each frame is one `<g class="fr">` in it. The newest shown frame hides the older ones. Each frame after the first has `data-step`. Put `<defs>` before the first frame. The code line follows the frame.

```css
.frames .fr:has(~ .fr.on) { visibility: hidden; opacity: 0; }
body.edit-active .frames .fr[data-step] { display: none; }
.lit { transition: color .3s ease; }
.slide[data-shown="0"] .lit.at0, .slide[data-shown="1"] .lit.at1,
.slide[data-shown="2"] .lit.at2, .slide[data-shown="3"] .lit.at3 { color: var(--acc); font-weight: 600; }
```

```html
<div class="two">
  <div class="panel"><div class="cap"><span>list.h</span><span class="side">69 · 83</span></div>
<pre><span class="lit at0">INIT_LIST_HEAD(list) { ... }</span>
__list_add(new, prev, next) { ... }
<span class="lit at1">list_add_tail(new, head)</span></pre></div>
  <div class="frames" id="SLOT-f">
    <svg viewBox="0 0 760 310" role="img" aria-label="..." style="width:100%;max-height:70vh;display:block">
      <defs>...</defs>
      <g class="fr">...</g>
      <g class="fr" data-step="1">...</g>
    </svg>
  </div>
</div>
<p class="punch" data-step="1">맨 앞도 맨 뒤도 결국 두 이웃 사이.</p>
```

A compare column:

```html
<div class="col panel accent" data-step="2">
  <div class="cap"><span>③ Linux list_head</span><span class="side">head 노드 1개</span></div>
  <svg viewBox="0 0 400 200" role="img" aria-label="..." style="width:100%;max-height:26vh;display:block">...</svg>
  <ul><li class="yes"><b>16 B</b> · 리스트와 노드가 <b>같은 타입</b></li></ul>
</div>
```

Each frame has a heading in the SVG: the call at the top in mono, and its expansion below in muted, with the resolved arguments in accent.

```html
<text x="0" y="28" font-family="var(--font-mono)" font-size="24" font-weight="600" fill="var(--ink)">list_add(&amp;C.list, &amp;ready_list)</text>
<text x="0" y="60" font-family="var(--font-mono)" font-size="20" fill="var(--mut)">= __list_add(C.list, <tspan fill="var(--acc)" font-weight="600">ready_list</tspan>, A.list)</text>
```

## Figure vocabulary

Square corners. No shadow, no gradient, no icon. Text in a node is mono. A Korean callout is `--font-body`, bold.

**Arrowheads.** One marker per color. Draw the arrow with a line and `marker-end`.

```html
<marker id="SLOT-k" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--ink)"/></marker>
<marker id="SLOT-r" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--acc)"/></marker>
```

**Nodes.** Height 80. The anchor is `--node`. A node from an earlier scene is white and ink. The new node is white and accent.

```html
<rect x="40"  y="160" width="150" height="80" fill="var(--node)" stroke="var(--ink)" stroke-width="2"/>
<rect x="260" y="160" width="150" height="80" fill="var(--paper)" stroke="var(--acc)" stroke-width="3"/>
<text x="335" y="210" text-anchor="middle" font-family="var(--font-mono)" font-size="24" font-weight="600" fill="var(--ink)">C.list</text>
```

**Doubly linked pair.** Two parallel arrows, 15 above and 15 below the node center. Leave a 5-unit gap at the arrowhead.

```html
<g stroke="var(--acc)" stroke-width="3" marker-end="url(#SLOT-r)">
  <line x1="190" y1="185" x2="255" y2="185"/>
  <line x1="260" y1="215" x2="195" y2="215"/>
</g>
```

**Ring closure.** One curve over the row and one curve under it. The ring is the point: always draw it.

```html
<g stroke="var(--ink)" stroke-width="2" fill="none" marker-end="url(#SLOT-k)">
  <path d="M775,160 C775,85 115,85 115,155"/>
  <path d="M115,240 C115,330 775,330 775,245"/>
</g>
```

**Self-loop, drawn in.** A pointer to its own node. The curve draws itself on the step, and the head and the answer appear after it. The placeholder (`next = ?`) is on screen first.

```css
.self path { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset .8s var(--ease); }
.self-a { opacity: 0; transition: opacity .25s ease; }
.self-q { transition: opacity .25s ease; }
.slide:not([data-shown="0"]) .self path { stroke-dashoffset: 0; }
.slide:not([data-shown="0"]) .self-a { opacity: 1; transition-delay: .6s; }
.slide:not([data-shown="0"]) .self-q { opacity: 0; }
```

```html
<g class="self" stroke="var(--acc)" stroke-width="3" fill="none">
  <path pathLength="1" d="M525,185 C650,185 650,75 450,75 L450,157"/>
  <path pathLength="1" d="M375,215 C250,215 250,330 450,330 L450,243"/>
</g>
<g class="self-q" font-family="var(--font-mono)" font-size="21" fill="var(--mut)"><text x="560" y="68">next = ?</text></g>
<g class="self-a" font-family="var(--font-mono)" font-size="21" font-weight="600" fill="var(--acc)"><path d="M441,140 L459,140 L450,158 z" stroke="none"/><text x="560" y="68">next = &amp;ready_list</text></g>
```

To use this, make the placeholder frame the first frame, and add one empty `data-step="1"` element to the slide, so that the step exists.

**Split node.** A struct with two fields. A divider and two muted labels.

```html
<rect x="50" y="62" width="120" height="60" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
<line x1="110" y1="62" x2="110" y2="122" stroke="var(--ink)" stroke-width="2"/>
<text x="80" y="98" font-size="15" text-anchor="middle" font-family="var(--font-mono)" fill="var(--mut)">prev</text>
<text x="140" y="98" font-size="15" text-anchor="middle" font-family="var(--font-mono)" fill="var(--mut)">next</text>
```

**Boundaries.** A dashed frame means "the fields of one struct". A solid muted frame on `--panel` means "another object holds this". Removing the frame is an argument: in the compare slide, the winner has no dashed frame.

```html
<rect x="30" y="22" width="340" height="128" fill="none" stroke="var(--ink)" stroke-width="2" stroke-dasharray="7 5"/>
<rect x="200" y="22" width="185" height="128" fill="var(--panel)" stroke="var(--mut)" stroke-width="2"/>
```

**NULL.** A dot, a line down, two short bars. Accent when NULL is the problem.

```html
<circle cx="160" cy="82" r="5" fill="var(--ink)"/>
<g stroke="var(--acc)" stroke-width="3"><line x1="160" y1="82" x2="160" y2="146"/><line x1="146" y1="146" x2="174" y2="146"/><line x1="152" y1="153" x2="168" y2="153"/></g>
```

**Size line.** Under a compare figure, the formula is muted and the result is large. The result is accent only when it is the problem.

```html
<text x="200" y="182" text-anchor="middle" font-family="var(--font-mono)" font-size="18" fill="var(--mut)">16 + 16 = <tspan font-size="22" font-weight="700" fill="var(--acc)">32 B</tspan></text>
```

**Memory layout.** One row is 8 bytes, 400 wide and 44 high. Offsets are to the left, in muted mono. A 4-byte field is 200 wide. A gap is hatched in accent, with a white plate under its label. In a frame after the change, draw the old gap with the same pattern in `--mut`. Fields that the talk does not need become one dashed row. The result (`sizeof = 288`) is at the bottom, at size 30.

```html
<pattern id="SLOT-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="var(--paper)"/><line x1="0" y1="0" x2="0" y2="8" stroke="var(--acc)" stroke-width="3"/></pattern>
<text x="78" y="231" text-anchor="end" font-family="var(--font-mono)" font-size="15" fill="var(--mut)">24</text>
<rect x="290" y="212" width="200" height="44" fill="url(#SLOT-hatch)" stroke="var(--acc)" stroke-width="3"/>
<rect x="370" y="221" width="40" height="26" fill="var(--paper)"/>
<text x="390" y="240" text-anchor="middle" font-family="var(--font-mono)" font-size="19" font-weight="600" fill="var(--acc)">빈틈</text>
<rect x="90" y="300" width="400" height="44" fill="var(--panel)" stroke="var(--ink)" stroke-width="2" stroke-dasharray="6 5"/>
<text x="290" y="328" text-anchor="middle" font-family="var(--font-mono)" font-size="15" fill="var(--mut)">⋯ lock_list · elem · tf ⋯</text>
```

**Scale block.** To show how small a thing is, draw the container tall and white, and fill only the true share with accent. Use one fill. Do not draw a cell for each unit, and do not fill with ink. For a count above 6, use the same block with a label for the share.

```html
<rect x="340" y="30" width="220" height="440" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
<rect x="340" y="438" width="220" height="32" fill="var(--acc)"/>
```

**Callout.** One thin accent line from the empty margin to the point, with a bold label at its tail. One per frame.

```html
<line x1="560" y1="150" x2="495" y2="234" stroke="var(--acc)" stroke-width="2" marker-end="url(#SLOT-r)"/>
<text x="566" y="142" font-family="var(--font-body)" font-size="19" font-weight="700" fill="var(--acc)">빈틈 4 B</text>
```

**Timeline tracks.** One track per person or branch. Left labels in mono. Open circles start a track. Filled circles mark an event on the main track. A wash band marks a shared span. Days are at the bottom in muted. On a step, one thick accent stroke paints the result, and thin accent arrows rise to the main track.

```css
.paint { stroke-dasharray: 145; stroke-dashoffset: 145; transition: stroke-dashoffset .9s var(--ease); }
.slide:not([data-shown="0"]) .paint { stroke-dashoffset: 0; }
```

```html
<rect x="455" y="112" width="845" height="165" fill="color-mix(in srgb, var(--acc) 8%, var(--paper))"/>
<line x1="290" y1="60" x2="1330" y2="60" stroke="var(--ink)" stroke-width="3"/>
<line x1="518" y1="135" x2="1290" y2="135" stroke="var(--ink)" stroke-width="2.5"/>
<circle cx="518" cy="135" r="6" fill="var(--paper)" stroke="var(--ink)" stroke-width="2.5"/>
<line class="paint" x1="1150" y1="255" x2="1290" y2="255" stroke="var(--acc)" stroke-width="9"/>
<g data-step="2" stroke="var(--acc)" stroke-width="2.5" marker-end="url(#SLOT-r)"><line x1="518" y1="187" x2="518" y2="70"/></g>
```

## Do not

- Do not write any hex value in the deck. Use `var(--…)`, so that the student can change the accent.
- Do not put accent on two things that the speaker does not talk through together.
- Do not use rounded corners, shadows, icons, or a dark panel.
- Do not change a frame's coordinates between scenes when the node stays. The audience tracks a node by its place. When a new node needs room, re-space the whole row once, on that step.
- Do not explain in a label what the speaker says. A label is a name, a value, or a size.
- Do not fit a figure by shrinking text. Split the slide (`reference/build.md`, density limits).
