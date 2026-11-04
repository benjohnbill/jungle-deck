---
version: alpha
name: Bsize Cast
description: Swiss white page, cobalt accent. A defect traced through real tool output. The record is the figure, and the accent marks what the speaker points at.
colors:
  canvas: "#ffffff"
  ink: "#0a0a0a"
  primary: "#1638c7"
  ink-mute: "#5e5e5e"
  surface: "#f3f5fc"
  hairline: "#ebebeb"
typography:
  display: { fontFamily: IBM Plex Sans KR, fontWeight: 700, letterSpacing: -0.02em, lineHeight: 1.22 }
  body: { fontFamily: IBM Plex Sans KR, fontWeight: 400, lineHeight: 1.5 }
  mono: { fontFamily: IBM Plex Mono, fontWeight: 400, lineHeight: 1.55 }
---

# Bsize Cast

Use this style for a talk that traces a defect from its symptom to its cause with real tool output: a debugger, a compiler, a test runner, a log.
Build on `templates/stage.html`. Do not change its runtime. Uncomment its IBM Plex `<link>` and font tokens. Map the colors with `reference/design.md` § Token mapping.

The Swiss base is the `stage.html` default: the 12-column grid, the head and foot rules, and square corners. This file covers what this style adds.

This style has no SVG, no image, and no icon. Every part is HTML text, so the student can edit it in place. The panel tint comes from `surface`, a light cobalt. Do not change it to gray.

## The one rule

**The real record is the figure. Accent marks only what the speaker points at**.

- `.hl` is the line that proves the point. Use it on one line, or on two adjacent lines.
- `.uline` is the token inside a line that the speaker compares with another token.
- `.c-hit` is a line that the speaker reads aloud, or a line that repeats to make a pattern.
- `.panel.accent` is the panel that holds the answer. A slide has at most one.
- `h2 em`, `.punch b`, and `.chain b` hold one value or one short phrase.

The accent is a text color. The only accent fills are `--hl` and the square in front of `.punch`.

The accent measures 8.66:1 on `--paper`, 7.95:1 on `--panel`, and 6.36:1 on `--hl`, so it is safe at every text size. `--dim` measures 3.43:1 on `--panel`. Use `.c-dim` only for an elided run, and never for evidence.

## Slides

| Slide | Parts |
|---|---|
| Symptom (cover) | `.kicker`, `h1` with one `<em>`, record panel, `.ask` |
| Trace | `h2`, `.said`, `.panels` with two evidence columns, `.chain` |
| Cause | `h2`, `.said`, diagnostic table, `.punch`, evidence column |
| Quiz | `h2`, `.panels.big`, no step, no `.punch` |
| Answer | `h2`, `.panels.fit` with two evidence columns, annotated panel |
| Close | two `h1`, `.rule`, `.thanks` |

Usual order: symptom, trace, cause, quiz, answer, close. The trace and the cause each take a quarter of the talk. The other slides are short.

The cover shows the failure at once. It has no decoration.
The `h2` is one short line. A question opens the cause and the quiz. A statement gives the answer.
`.head`: the tool and its input on the left (`gdb · coalescing-bal.rep`). The number is on the right.
`.foot`: the commands that produced the record, or one line that keeps the claim exact (`24는 bsize()의 값 · malloc(4GB+16)은 가드에서 NULL`).

Use at most 4 steps on a slide. The steps follow the speaker's reasoning: the doubt, the record, the reading, the cause.

## CSS to add

Add this to the deck `<style>`. These rules are not in `stage.html`, or they change its default. Each part below adds its own CSS.

```css
.kicker { color: var(--mut); border: 0; padding: 0; letter-spacing: 0; text-transform: none; }
.thanks { font-family: var(--font-body); }
.col { display: flex; flex-direction: column; gap: clamp(.35rem, 1vh, .8rem); min-width: 0; }
```

## Figure vocabulary

The panel from `stage.html` is the main shape. Code and tool output sit in the same light panel, so `.cap` tells them apart.

**Record panel.** Paste real output without a change, and put `data-evidence` on the `<pre>`. The `.cap` left side names the tool and the command. The `.side` label is `실제 기록` only for output that the student really ran. For source code, `.side` names its role: `타입`, `가드`, `주석`.

```html
<div class="panel">
  <div class="cap"><span>mdriver · coalescing-bal.rep</span><span class="side">실제 기록</span></div>
<pre class="wrap" data-evidence>ERROR: mem_sbrk failed. Ran out of memory...
Checking mm_malloc for correctness, ERROR [trace 0, line 7673]: mm_malloc failed.</pre>
</div>
```

**Symptom cover.** The cover holds the failure itself. The `.ask` line under it restates the failure in a few plain words. The `.kicker` is a muted line with no box.

```html
<span class="kicker">Week NN · 과제 이름</span>
<h1><em>Type Casting</em> - 컴파일러가 통과시켜주는 오류</h1>
<div class="panel">...the record panel...</div>
<p class="ask">- 20MB가 바닥났어요</p>
```

**Elided run.** To cut a long record, keep the first rounds and the last round. One muted line states how many rounds it removed. The count is part of the evidence. It keeps the panel at 10 lines.

```html
<pre data-evidence>mem_sbrk(4104)  heap = 4120 bytes
<span class="c-hit">#1  extend_heap (size=4095) at mm.c:175</span>

mem_sbrk(8200)  heap = 8224 bytes
<span class="c-hit">#1  extend_heap (size=8190) at mm.c:175</span>

<span class="c-dim">   ⋮   같은 패턴 7,670번</span>

mem_sbrk(4104)  heap = <span class="c-hit">20969440</span> bytes
<span class="c-hit">#1  extend_heap (size=4095) at mm.c:175</span></pre>
```

**Highlight band.** `.hl` is `display: block` in `stage.html`, so it ends its own line. Write the next line directly after `</span>`, with no line break. A line break here shows as an empty row. Keep the next line's indent.

```html
<pre>void *mm_malloc(size_t size){
<span class="hl">    if (size == 0 || size &gt;= MAX_HEAP){   // MAX_HEAP = 20MB</span>        return NULL;
    }</pre>
```

Two adjacent bands, the raw value and then the value that the code used:

```html
<span class="hl"> 4 bsize         = {unsigned int (size_t)} 0x555555557c88 &lt;bsize&gt;</span><span class="hl"> 5 (size_t)bsize = 93824992246920</span>
```

**Drawn underline.** A cobalt line draws from left to right under a token when its step appears. Use it to tie two tokens together. The first delay waits for the panel to finish its reveal. `.uline-2` draws the second token after the first. Put the token inside a `data-step` element, or the line never draws.

```css
.uline {
  background: linear-gradient(var(--acc), var(--acc)) no-repeat left 100% / 0% 3px;
  padding-bottom: 2px; color: var(--acc); font-weight: 600;
  transition: background-size .9s var(--ease) .45s;
}
.on .uline, .uline.on { background-size: 100% 3px; }
.uline-2 { transition-delay: .9s; }
```

```html
<div class="col" data-step="4">
  <div class="panel">
    <div class="cap"><span>mm.c</span><span class="side">타입</span></div>
<pre>#define GET_SIZE(bp)  ((<span class="uline">unsigned int</span>)(...))
static <span class="uline uline-2">unsigned int</span> bsize(size_t psize)</pre>
  </div>
  <p class="punch">그러나.. 애초에 둘 다 <b>unsigned int</b>였다.</p>
</div>
```

**Evidence column.** A panel and the sentence that reads it, as one step. The step is on `.col`, so the panel and its reading arrive together. The panel shows the record. The `.punch` under it says what the record means. Two `.punch` lines are fine when the second line is its own step.

```html
<div class="col" data-step="3">
  <div class="panel accent">...the record panel...</div>
  <p class="punch"><b>8208</b>바이트 빈 블록이 바로 앞에 있는데, 비교 대상이 <b>93조.</b></p>
  <p class="punch" data-step="4">함수 포인터 <code>bsize</code>를 <code>(size_t)</code>로 바꾼 값</p>
</div>
```

**Content-width panels.** A panel is as wide as its code, so the lines do not float in empty space. In `.fit`, both panels stretch to one height, so the sentences under them line up. In `.trace`, the left panel is as wide as its code, and the right panel takes the rest.

```css
.panels.fit { grid-template-columns: max-content max-content; justify-content: start; align-items: stretch; }
.panels.fit > .col > .panel { flex: 1; }
.panels.trace { grid-template-columns: max-content minmax(0, 1fr); }
```

```html
<div class="panels trace">
  <div class="col" data-step="2">...</div>
  <div class="col" data-step="3">...</div>
</div>
```

**Said line.** What the speaker thought at that moment, as the first step of a slide. It is larger than the body, with cobalt quote marks. It carries the doubt, so the `h2` does not need to.

```css
.said { font-size: clamp(1.15rem, 1.6vw, 2.3rem); font-weight: 500; line-height: 1.4; }
.said::before { content: "“"; color: var(--acc); font-weight: 700; margin-right: .1em; }
.said::after  { content: "”"; color: var(--acc); font-weight: 700; margin-left: .1em; }
```

```html
<p class="said" data-step="1">왜 메모리가 계속 늘어났을까?</p>
```

**Verdict chain.** One or two lines in mono that evaluate the comparison with the real values. An accent bar is on the left. It sits directly under the record, and its `<b>` holds each result.

```css
.chain { font-family: var(--font-mono); font-size: var(--code-size); line-height: 1.5;
         border-left: 3px solid var(--acc); padding: .15em 0 .15em .7em; }
.chain span { white-space: nowrap; }
.chain b { color: var(--acc); font-weight: 600; }
```

```html
<p class="chain"><span>8208 &gt;= 93824992246920 → <b>거짓</b></span><br><span>→ first_fit() = NULL → <b>extend_heap()</b></span></p>
```

**Diagnostic table.** Two versions of one line, and what the tool said about each. The row with the warning has a squiggle, which copies an editor's underline. The silent row is `tr.hit`: the missing warning is the point, so the row with no message gets the accent. The squiggle uses the accent, not red.

```css
.rows td.code { font-family: var(--font-mono); white-space: nowrap; }
.rows td.msg { font-family: var(--font-mono); font-size: .88em; }
.squiggle { text-decoration: underline wavy var(--acc); text-underline-offset: .22em; text-decoration-thickness: 1.5px; }
```

```html
<table class="rows" data-step="2">
  <tr><th>first_fit() 의 조건</th><th>에디터 (clangd)</th></tr>
  <tr><td class="code">GET_SIZE(bp) &gt;= <span class="squiggle">bsize</span></td><td class="msg">Ordered comparison between pointer and integer</td></tr>
  <tr class="hit"><td class="code">GET_SIZE(bp) &gt;= (size_t)bsize</td><td class="msg">진단 없음 (gcc -Wall도 0개)</td></tr>
</table>
```

**Quiz panel.** A question that the audience can solve from the panel. The code is larger, the `.side` label is `?`, and the slide has no step and no `.punch`. The answer is on the next slide. `.sig` is a highlight inside a line, for the types that hold the trick. The second panel gives only the constants the audience needs.

```css
.panels.big { grid-template-columns: minmax(0, max-content) max-content; justify-content: start; align-items: stretch; }
.big pre { font-size: clamp(.95rem, min(1.4vw, 2.5vh), 2.2rem); }
.sig { background: var(--hl); color: var(--acc); font-weight: 600; padding: 0 .15em; }
```

```html
<h2><em>unsigned int</em> 타입의 <em>bsize(4GB + 16)</em>은 몇일까?</h2>
<div class="panels big">
  <div class="panel accent">
    <div class="cap"><span>mm.c · bsize()</span><span class="side">?</span></div>
<pre>static <span class="sig">unsigned int</span> bsize(<span class="sig">size_t psize</span>){
    return HSIZE + <span class="c-hit">(unsigned int)</span>exact_psize(psize) + FSIZE;
}</pre>
  </div>
  <div class="panel">
    <div class="cap"><span>상수</span></div>
<pre>HSIZE = FSIZE = 4

<span class="hl">UINT_MAX = 2³² − 1   // 약 4GB</span></pre>
  </div>
</div>
```

**Annotated panel.** The last step of the answer. It proposes the fix as a comment in the code, in `.c-hit`. The panel hugs its text. The panel does not take the full width.

```html
<div class="col" data-step="3">
  <div class="panel" style="align-self:flex-start">
    <div class="cap"><span>mm.c · exact_psize() · 제안</span><span class="side">주석</span></div>
<pre><span class="c-hit">/* MAX_HEAP(20MB) 가드가 있어서 4GB를 넘는 크기는 여기 오지 않는다.
   가드가 없다면 이 캐스트는 크기를 잘라 낸다. */</span>
return (unsigned int)psize;</pre>
  </div>
  <p class="punch">그래도 <b>왜 괜찮은지</b> 주석으로 남겨 두는 게 좋지 않을까?</p>
</div>
```

**Two-line close.** `stage.html` already styles this. The first `h1` is ink and states the lesson. The second `h1` is accent and states the habit. The slide has no step.

```html
<h1>컴파일러가 조용한 건, 내가 조용히 시켰기 때문일 수 있다.</h1>
<h1>조용히 시켰다면, 왜 그래도 되는지 적어 둔다.</h1>
<div class="rule"></div>
<p class="thanks">감사합니다</p>
```

## Do not

- Do not write any hex value in the deck. Use `var(--…)`, so that the student can change the accent.
- Do not write `실제 기록` on output that the student did not run, and do not tidy a real record. Cut it only with an elided run.
- Do not draw a diagram of what a record already shows.
- Do not use a dark terminal band, rounded corners, shadows, icons, or a gradient fill.
- Do not put two `.panel.accent` on one slide.
- Do not put the quiz answer on the quiz slide.
- Do not explain in a panel. The reading goes in `.punch`, and the doubt goes in `.said`.
- Do not fit a record by shrinking `pre` below `--code-size`, and do not add a scale-to-fit script. Cut to 10 lines per panel, or split the slide (`reference/build.md`, density limits).
