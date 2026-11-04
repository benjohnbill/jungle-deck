---
version: alpha
name: OOP in C
description: Swiss white page. Code panels are the figure. One dark panel holds what the compiler or linker said, and light panels hold what a person wrote.
colors:
  canvas: "#ffffff"
  ink: "#0a0a0a"
  primary: "#ff3300"
  ink-mute: "#6b6b6b"
  surface: "#f7f7f5"
  hairline: "#ebebeb"
  machine: "#14171c"
  machine-ink: "#d5d1c9"
  machine-rule: "#3a3f47"
  machine-side: "#e0a458"
  machine-err: "#ff6a3d"
  machine-dim: "#7e858f"
  machine-ok: "#8fbf8f"
typography:
  display: { fontFamily: IBM Plex Sans KR, fontWeight: 700, letterSpacing: -0.02em, lineHeight: 1.2 }
  body: { fontFamily: IBM Plex Sans KR, fontWeight: 400, lineHeight: 1.5 }
  mono: { fontFamily: IBM Plex Mono, fontWeight: 400, lineHeight: 1.6 }
---

# OOP in C

Use this style for a talk whose proof is source code and tool output: a compiler error, a linker result, a header that two files share.
Build on `templates/stage.html`. Do not change its runtime. Uncomment its IBM Plex `<link>` and font tokens. Map the six base colors with `reference/design.md` § Token mapping.

The base is the Swiss page of `stage.html`: white paper, 12-column grid, head and foot bands, one accent. This file spends its length on the panels. Most figures here are HTML, so the student can edit their text in edit mode. SVG text is locked, so this style uses one SVG per talk.

The SVG below follows `vendor/diagram-design/SKILL.md` § Slide-scale overrides. Prefix each `id` with the slot id; `SLOT` below is that prefix. Coordinates are examples: keep the font sizes and stroke widths, and re-space the shapes to fit.

## The one rule

**Dark panel = the machine said it. Light panel = a person wrote it**.

- Compiler errors, object bytes, and tool output go in a dark panel. Source code and headers go in a light panel.
- Most slides have no dark panel. A slide has two only when it compares a before and an after.
- A dark panel holds real output. Put `data-evidence` on its `<pre>`. Output that you did not run does not go in a dark panel.
- Code that you made up for the talk stays in a light panel, and its caption says that it is an example.
- Amber, green, and the softer error red appear only in a dark panel. On the page, the accent is the only hue.
- In a light panel, the accent means "look here". Mark the word with `.c-hit`, not the line. This style does not use `.hl`.
- A slide has one `.panel.accent`: the panel that the argument stands on. When two files share a header, the header is that panel.

The accent is 3.42:1 on `--panel`. In the SVG, accent text is weight 600 or more at size 19 or more.

## Slides

| Slide | Parts |
|---|---|
| Cover | `.tags`, `h1` with one `<em>`, `.rule`, `.sub` (one word), `.dot` |
| Map | thesis, one SVG (dashed zones, title-bar nodes, one private definition), `.punch` |
| Proof | thesis, `.two` (`.stack` of light panels, one machine panel), `.punch` |
| Build | thesis, `.flow` (light panels above, machine panels below), `.punch`, step dot |
| Callback | thesis as code, `.cb` (one panel per step), `.punch` on the last step, step dot |
| Why | thesis, `.two.wide-r` (`.stack` of what each side does not know, swap call), `.punch` |
| Close | `h1` that restates the cover as an answer, `.rule`, `.takeaway` |

Usual order: cover, map, proof, build, callback, why, close.
The thesis is small (`--h3-size`). The panels are the slide. The audience reads the map for five seconds, and the speaker does not explain it.
`.head`: the section name or the identifier on the left, with its case kept. `.foot`: the files on the slide, the build line, or the standard clause that proves the slide. The cover foot has the talk length on the right.

## CSS to add

Add this to the deck `<style>`. These rules are not in `stage.html`. The code size is larger than the `stage.html` default: the panels are the figure.

Add seven tokens to `:root`, with the values of the front matter keys. They do not derive from the accent. `--m-bg` = `machine`, `--m-ink` = `machine-ink`, `--m-rule` = `machine-rule`, `--m-side` = `machine-side`, `--m-err` = `machine-err`, `--m-dim` = `machine-dim`, `--m-ok` = `machine-ok`.

```css
:root { --code-size: clamp(.85rem, min(1.4vw, 2.4vh), 2.1rem); } pre { line-height: 1.6; }
h2.thesis { font-size: var(--h3-size); max-width: none; } h2.thesis b { color: var(--acc); }
.panel > .cap { background: var(--paper); color: var(--ink); padding: .2em .7em; border-bottom-color: var(--panel-b); }
.panel > .cap .side { color: var(--mut); font-weight: 400; }
.panel.accent > .cap { border-bottom-color: var(--acc); } .panel.accent > .cap .side { color: var(--acc); }
.two { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(.6rem, 1.6vw, 1.4rem); align-items: start; }
.two.wide-r { grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr); }
.stack { display: flex; flex-direction: column; gap: clamp(.45rem, 1.2vh, .9rem); min-width: 0; }
.tags { display: flex; gap: .7em; } .eyebrow { font-family: var(--font-mono); font-size: var(--small-size); letter-spacing: .2em; text-transform: uppercase;
           color: var(--paper); background: var(--acc); border: 2px solid var(--acc); padding: .35em .75em; }
.eyebrow.ghost { text-transform: none; letter-spacing: .04em; color: var(--acc); background: var(--paper); }
.sub { color: var(--mut); font-size: clamp(1.1rem, 1.5vw, 2.1rem); line-height: 1.6; max-width: 38ch; }
.dot { position: absolute; right: var(--slide-padding); top: 50%; transform: translateY(-50%);
       width: clamp(36px, 5.5vw, 68px); aspect-ratio: 1; border-radius: 50%; background: var(--acc); }
.step-dot { position: absolute; right: var(--slide-padding); bottom: calc(clamp(1rem, 3vh, 2.2rem) + 2.4rem); width: clamp(9px, .7vw, 14px); aspect-ratio: 1;
            border-radius: 50%; background: var(--acc); z-index: 3; animation: breathe 1.9s ease-in-out infinite; }
.slide:not(:has([data-step]:not(.on))) .step-dot { display: none; }
@keyframes breathe { 50% { opacity: .25; } }
.machine { border-color: var(--ink); background: var(--m-bg); }
.machine > .cap { background: var(--m-bg); color: var(--m-ink); border-bottom-color: var(--m-rule); }
.machine > .cap .side { color: var(--m-side); } .machine pre { color: var(--m-ink); }
.m-err { color: var(--m-err); font-weight: 600; } .m-dim { color: var(--m-dim); } .m-ok  { color: var(--m-ok); font-weight: 600; }
.ok { color: var(--ink); font-weight: 700; } .ng { color: var(--acc); font-weight: 700; }
.flow { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1.1fr) auto minmax(0, 1fr);
        column-gap: clamp(.4rem, .9vw, .9rem); row-gap: clamp(.25rem, .8vh, .6rem); align-items: center; }
.flow pre { font-size: clamp(.85rem, min(1.3vw, 2.3vh), 2rem); }
.flow .arrow, .flow .down { font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); white-space: nowrap; }
.flow .down { text-align: center; } .flow .down b, .flow .link b { color: var(--acc); font-weight: 600; }
.flow .f-main { grid-area: 1 / 1; } .flow .a1 { grid-area: 1 / 2; } .flow .f-h  { grid-area: 1 / 3; }
.flow .a2     { grid-area: 1 / 4; } .flow .f-rc { grid-area: 1 / 5; } .flow .d1     { grid-area: 2 / 1; } .flow .d2 { grid-area: 2 / 5; }
.flow .f-mo   { grid-area: 3 / 1; } .flow .link { grid-area: 3 / 2 / 4 / 5; } .flow .f-ro { grid-area: 3 / 5; }
.flow .link { display: flex; align-items: center; gap: .6em; font-family: var(--font-mono); font-size: var(--small-size);
              color: var(--acc); white-space: nowrap; }
.flow .link i { flex: 1; height: 2px; background: var(--acc); }
.cb { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(.5rem, 1.4vw, 1.2rem); align-items: start; }
.cb .cb-h { grid-column: 1 / 3; }
h2.thesis code { font-family: var(--font-mono); font-weight: 600; letter-spacing: 0; }
.takeaway { border: 2px solid var(--ink); padding: clamp(.8rem, 2vh, 1.4rem) clamp(.9rem, 1.8vw, 1.6rem); max-width: 58ch;
            font-size: clamp(1rem, 1.28vw, 1.85rem); line-height: 1.7; }
.takeaway .k { display: block; font-family: var(--font-mono); font-size: var(--small-size); letter-spacing: .18em;
               text-transform: uppercase; color: var(--acc); margin-bottom: .5em; }
.takeaway b { color: var(--acc); }
.takeaway small { color: var(--mut); font-size: .8em; }
```

## Figure vocabulary

Square corners. No shadow, no gradient, no icon. The cover dot and the step dot are the only circles. Text in a panel or a node is mono, unless it is Korean prose.

A panel keeps its place from the start, and a step only makes it visible. An arrow and the panel it points to share one step number. The last step often brings the `.punch`.

**Step dot.** A small breathing accent dot above the right end of the foot rule tells the speaker that the slide has more steps. It goes out on the last step. Add it only to a slide with steps.

```html
<div class="step-dot" aria-hidden="true"></div>
```

**Citation caption.** A panel names its file on the left and its line range on the right. The range is real, so the audience can find the code. In a light panel the range is muted. In an accent panel it is accent.

```html
<div class="panel accent"><div class="cap"><span>main.c</span><span class="side">51 · 83</span></div>
<pre>Rec *<span class="c-hit">r</span> = new_record();
<span class="c-dim">...</span>
Read_total(<span class="c-hit">r</span>, print_total);</pre>
</div>
```

**Machine panel.** A near-black panel beside light panels. It has the look of a terminal, and it marks the one voice on the slide that is not the speaker's. The caption says which tool ran and on what. The right side of the caption is amber.

```html
<div class="panel machine"><div class="cap"><span>gcc · main.c 에서 구조체 내부를 보면</span><span class="side">error</span></div>
<pre data-evidence>r-&gt;count;

<span class="m-err">error:</span> invalid use of
  incomplete typedef ‘Rec’</pre>
</div>
```

**Byte patch.** Two machine panels show the same instruction before and after a tool. The instruction name is dim. Only the bytes that changed have color: error red before, green after. The captions are the tool stage.

```html
<div class="panel machine f-mo"><div class="cap"><span>main.o</span><span class="side">링크 전</span></div>
<pre data-evidence><span class="m-dim">call new_record</span>
e8 <span class="m-err">00 00 00 00</span></pre>
</div>
<div class="panel machine f-ro"><div class="cap"><span>study</span><span class="side">링크 후</span></div>
<pre data-evidence><span class="m-dim">call new_record</span>
e8 <span class="m-ok">41 02 00 00</span></pre>
</div>
```

**O and X marks.** One bold letter at the end of a code line says whether the line is legal in this file. O is ink. X is accent. Align the two letters with spaces.

```html
<pre>Rec *r = new_record();  <span class="ok">O</span>
r-&gt;count;               <span class="ng">X</span></pre>
```

**Build flow.** A five-column HTML grid draws a pipeline with real code in its boxes. The top row is the source files, with text arrows between them. The middle row is `compile ▼`. The bottom row is the object file on the left and the linked file on the right. Each box has a fixed grid cell, so a step can add a panel without a shift.

```html
<div class="flow">
  <div class="panel f-main">...</div>
  <div class="arrow a1" data-step="1">include ▶</div>
  <div class="panel accent f-h" data-step="1">...</div>
  <div class="arrow a2" data-step="2">◀ include</div>
  <div class="panel f-rc" data-step="2">...</div>
  <div class="down d1"><b>①</b> compile ▼</div>
  <div class="down d2" data-step="2"><b>①</b> compile ▼ record.o</div>
  <div class="panel machine f-mo">...</div>
  <div class="link">...</div>
  <div class="panel machine f-ro">...</div>
</div>
```

**Link arrow.** One long arrow across the empty middle of the bottom row, built from HTML: a line, a label, a line, a head. It is accent, and it is the only accent arrow on the slide. The label says what the tool does, in one clause.

```html
<div class="link"><i></i><span><b>②</b> link · 0을 new_record까지의 거리로 채운다</span><i></i>▶</div>
```

**Shared-shape grid.** A full-width accent panel holds the contract that two files share. The two files sit under it, side by side, at equal size. The shape of the grid is the argument: one contract above, two parties below. Show the contract first, then each party on its own step.

```html
<div class="cb">
  <div class="panel accent cb-h" data-step="1">
    <div class="cap"><span>record.h</span><span class="side">27 – 28</span></div>
<pre>typedef void (*<span class="c-hit">Minutes</span>)(int minutes);
void Read_total(const Rec *r, <span class="c-hit">Minutes func</span>);</pre>
  </div>
  <div class="panel" data-step="2">...</div>
  <div class="panel" data-step="3">...</div>
</div>
<p class="punch" data-step="3"><code>record.c</code>는 <b>언제</b> 부를지만 알고, <b>무엇을</b> 할지는 <code>main</code>이 정한다</p>
```

**Comment as evidence.** To prove that something is absent, show the top of the file dim and state the absence in one comment. Then the only `.c-hit` in the panel is the line that does the work.

```html
<pre><span class="c-dim">#include "record.h"</span>   <span class="c-com">// stdio.h 없음</span>

void Read_total(const Rec *r, Minutes func){
    <span class="c-dim">...</span> <span class="c-hit">func(total);</span>
}</pre>
```

**Ignorance stack.** Three one-line panels, stacked. The caption is a sentence about what each side does not know, and the side label names the topic. The code line is only the names that side cannot see. The third panel is accent and holds what the two sides share.

```html
<div class="stack">
  <div class="panel"><div class="cap"><span>main.c 가 모르는 것</span><span class="side">저장 방식</span></div><pre>r-&gt;list · count · capacity</pre></div>
  <div class="panel"><div class="cap"><span>record.c 가 모르는 것</span><span class="side">출력 방식</span></div><pre>printf · stderr</pre></div>
  <div class="panel accent"><div class="cap"><span>record.h</span><span class="side">둘이 공유하는 모양</span></div><pre>typedef void (*Minutes)(int);</pre></div>
</div>
```

**Swap call.** Two call lines, aligned, with one argument changed. The changed argument is `.c-hit`. A short comment names the result of each line. The new function is above them, in the same panel.

```html
<div class="panel"><div class="cap"><span>main.c</span><span class="side">예시</span></div>
<pre>void <span class="c-hit">print_total_err</span>(int minutes){
    fprintf(<span class="c-hit">stderr</span>, "Total: %d minutes\n", minutes);
}

Read_total(r, print_total);      <span class="c-com">// stdout</span>
Read_total(r, <span class="c-hit">print_total_err</span>);  <span class="c-com">// stderr</span></pre></div>
```

**Code thesis.** When the slide is about one call, that call is the thesis, in mono, with its one argument in accent. The sentence after it is short.

```html
<h2 class="thesis"><code>Read_total(r, <b>print_total</b>)</code> 은 더 재미있다</h2>
```

**Dashed zones.** The map splits the files by owner. Each owner is one dashed frame with a bold muted name above it. The frames carry no fill. Set the viewBox to `0 0 1160 440`. Style the SVG `width:100%;height:auto;max-height:62vh;display:block`.

```html
<rect x="8" y="36" width="270" height="396" fill="none" stroke="var(--mut)" stroke-width="2" stroke-dasharray="8 6"/>
<text x="20" y="24" font-family="var(--font-body)" font-size="20" font-weight="700" fill="var(--mut)">CLI 쪽 (interface)</text>
```

**Title-bar node.** A node looks like a small code panel: `--panel` fill, a 1.5 divider, the file name in the bar, and two lines of content under it. The `--panel` fill is decoration, so the stroke and the label carry the node. The content line that matters is ink. The list of names under it is muted.

```html
<rect x="362" y="64" width="300" height="140" fill="var(--panel)" stroke="var(--ink)" stroke-width="2"/>
<line x1="362" y1="100" x2="662" y2="100" stroke="var(--ink)" stroke-width="1.5"/>
<text x="374" y="89" font-family="var(--font-mono)" font-size="19" font-weight="500" fill="var(--ink)">record.h</text>
<text x="376" y="140" font-family="var(--font-mono)" font-size="19" fill="var(--ink)">typedef … Rec;</text>
<text x="376" y="178" font-family="var(--font-mono)" font-size="17" fill="var(--mut)">new_record · Read_total …</text>
```

**Private definition.** One node on the map has an accent stroke, and its first content line is accent. That node holds the thing that nothing else can see. It is the only accent in the figure. The divider is accent, and the file name stays ink.

```html
<rect x="820" y="64" width="312" height="140" fill="var(--panel)" stroke="var(--acc)" stroke-width="3"/>
<text x="834" y="140" font-family="var(--font-mono)" font-size="20" font-weight="600" fill="var(--acc)">struct _Record {</text>
```

**Include arrows.** All arrows point at the headers, so the picture shows that no file reaches into another file. They are one ink group with one marker. One muted legend at the bottom right names the encoding.

```html
<marker id="SLOT-k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--ink)"/></marker>
<g stroke="var(--ink)" stroke-width="2" fill="none" marker-end="url(#SLOT-k)">
  <line x1="256" y1="200" x2="356" y2="140"/>
  <line x1="820" y1="134" x2="668" y2="134"/>
</g>
<text x="1140" y="422" text-anchor="end" font-family="var(--font-body)" font-size="16" fill="var(--mut)">화살표 = #include</text>
```

**Checklist box.** The close has one ink-bordered box. A small accent label is on top. Each line is one habit with its accent word, and a small muted term follows it.

```html
<div class="takeaway">
  <span class="k">체크 항목</span>
  헤더에 <b>이름만</b> 두면 정의부분을 숨길 수 있습니다. <small>불완전 타입</small><br>
  할 일은 <b>함수 포인터</b>로 넘깁니다. <small>콜백</small>
</div>
```

## Do not

- Do not put source code in a dark panel, and do not put made-up output in one.
- Do not use a dark caption band on a light panel. The caption is thin, on white, with one rule under it.
- Do not draw in SVG what a panel can show. Keep one SVG in the talk: the map.
- Do not uppercase a file name, a program name, or an identifier. The `.eyebrow` is uppercase only for plain words; use `.ghost` for a name.
- Do not move a panel between steps. The audience tracks a file by its place.
- Do not write any hex value in the deck outside the `:root` tokens.
- Do not fit a panel by shrinking text. Split the slide (`reference/build.md`, density limits).
