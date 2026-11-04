---
version: alpha
name: Array in C
description: Swiss white page, one signal color, no diagram. Real source code is the figure. It holds still while a step changes single tokens.
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

# Array in C

Use this style for a talk that walks through real code to one bug and its cause.
Build on `templates/stage.html`. Do not change its runtime. Uncomment its IBM Plex `<link>` and font tokens. Map the colors with `reference/design.md` § Token mapping.

This talk has no SVG. Every figure is HTML text, so the student can edit each word in edit mode.

## The one rule

**The code holds still. A step changes only tokens.** The audience reads one source file for the whole talk, so no line may jump.

- A step replaces text in its own place. Lines that do not change exist once in the DOM.
- Space for a later mark is reserved from the start: a transparent border, an empty row.
- The accent means "read here". It marks a token, not a line, and not a block of text.
- The panel that the speaker talks through is `.panel.accent`. Other panels are ink.
- The reference column stays at the same place on each slide and has no accent.
- A thesis holds one `<b>` accent phrase.

The accent is 3.67:1 on white. Use accent code only at weight 600 or more, in the large source panel. Small code uses weight only.

## Slides

| Slide | Parts |
|---|---|
| Cover | `.eyebrow`, `h1` with the claim in one `<em>`, `.rule`, `.sub` (the file name), `.dot` |
| Quiz | thesis as a question, `.mirror`, `.punch` on step 1, `.step-dot` |
| Work | thesis, `.work` (`.col.src` with a `.punch` under the code, `.col.ref`) |
| Turn | thesis, `.work` with `.args`, `.swap`, `.peek`, `.punch` on step 1, `.step-dot` |
| Evidence | plain `h2` with one `<em>`, `.panels.trio`, `.punch` |
| Close | the cover `h1` again, `.rule`, `.takeaway` |

Usual order: cover, quiz, work, work, turn, evidence, close. Each work slide shows one chunk of the same file.
The thesis is small (`--h3-size`). The evidence `h2` is the only larger headline between cover and close, so its size marks the climax.
Hold each panel to 8–10 lines. Cut code with a reduced code label (below).
`.foot`: the source file on a work slide, and one short line of the point on the quiz and evidence slides. The cover foot has the talk length on the right. The close foot has the date.

## CSS to add

Add this to the deck `<style>`. These classes are not in `stage.html`.

```css
h2.thesis { font-size: var(--h3-size); letter-spacing: -.01em; max-width: none; }
h2.thesis b { color: var(--acc); }
.sub { color: var(--mut); font-size: clamp(1.1rem, 1.5vw, 2.1rem); line-height: 1.6; max-width: 38ch; }
.eyebrow { align-self: flex-start; font-family: var(--font-mono); font-size: var(--small-size); letter-spacing: .2em; text-transform: uppercase; color: var(--paper); background: var(--acc); padding: .35em .75em; }
.dot { position: absolute; right: var(--slide-padding); top: 50%; transform: translateY(-50%); width: clamp(36px, 5.5vw, 68px); aspect-ratio: 1; border-radius: 50%; background: var(--acc); }
.panels { align-items: stretch; }
.panel { display: flex; flex-direction: column; } pre { flex: 1; }
```

## Figure vocabulary

Square corners. No shadow, no gradient, no icon, no SVG. A panel border is 2px. The dot on the cover and the dot for steps are the only circles.

**Inverted caption.** Each panel has a solid band. The left side is the file and function. The right side is the line range or a one-word role. The accent panel has an accent band. This replaces the light caption of `stage.html`. `## The turn slide` shows the markup.

```css
.panel > .cap { background: var(--panel-b); color: var(--paper); border-bottom: 0; letter-spacing: .08em; }
.panel.accent > .cap { background: var(--acc); }
.panel.accent > .cap .side { color: var(--paper); }
```

**Token mark.** Wrap only the token that the speaker names. A comparison marks the operator and the operand, not the parentheses. A comment is `.c-com`, a line that the talk skips is `.c-dim`.

```html
<pre>return (arr <span class="c-hit">== bb1</span>) ? 6 : <span class="c-hit">0</span>;</pre>
```

**Swap in place.** The before text and the after text sit in one grid cell inside the `<pre>`, so the height does not change. The before text leaves fast. The after text enters a little later and slower. The after text has the `data-step`, so the swap can happen on any step. In edit mode, only the current state shows, so the student can step to a state and edit it. A swap of many lines starts at column 0 and holds only the changed lines, as in `## The turn slide`.

```css
.swap { display: inline-grid; vertical-align: top; }
.swap > * { grid-area: 1 / 1; white-space: pre; }
.swap > .st-b { transition: opacity .15s cubic-bezier(.4, 0, 1, 1), transform .15s cubic-bezier(.4, 0, 1, 1); }
.swap > .st-a { transform: translateY(.35em); transition: opacity .26s cubic-bezier(0, 0, .2, 1) .1s, transform .26s cubic-bezier(0, 0, .2, 1) .1s; }
.swap > .st-a.on { transform: none; }
.swap:has(> .st-a.on) > .st-b { opacity: 0; transform: translateY(-.35em); }
body.edit-active .swap > .st-a:not(.on) { display: none; }
body.edit-active .swap:has(> .st-a.on) > .st-b { display: none; }
.c-ans { color: var(--acc); font-weight: 700; }
```

```html
<pre>void show(<span class="swap"><span class="st-b c-hit">int arr[]</span><span class="st-a c-ans" data-step="1">int *arr</span></span>) {
    sizeof(arr);      <span class="swap"><span class="st-b c-com">// ?</span><span class="st-a c-ans" data-step="1">// 8</span></span>
}</pre>
```

**Work layout.** Two columns: the source at left, the reference at right. Both tops align. The code size follows the scarcer of width and height, so a low screen does not clip code. Choose the size class by chunk length.

```css
.work { flex: 0 1 auto; min-height: 0; display: grid; grid-template-columns: minmax(0, 1.72fr) minmax(0, 1fr); gap: clamp(.6rem, 1.4vw, 1.3rem); }
.work > * { min-height: 0; min-width: 0; }
.col { display: flex; flex-direction: column; gap: clamp(.45rem, 1.2vh, .9rem); min-height: 0; }
.col.src pre { line-height: 1.6; }
.col.src.zoom-b pre { font-size: clamp(.95rem, min(1.36vw, 2.3vh), 2.05rem); } /* short chunks */
.col.src.zoom-c pre { font-size: clamp(.95rem, min(1.3vw, 2.12vh), 2.05rem); } /* 10 lines */
```

**Quiet reference column.** Input and expected output stay on screen across the work slides. Repeat the same markup on each slide, so the column does not move between them. The code is small. A mark is bold ink, not accent. The caption side is a role in capitals (`INPUT`, `EXPECTED`).

```css
.col.ref pre { font-size: clamp(.85rem, 1vw, 1.45rem); line-height: 1.58; }
.col.ref .cap { font-size: clamp(.75rem, .8vw, 1.15rem); }
.col.ref .c-hit { color: var(--ink); font-weight: 600; }
.col.ref .panel:not(.accent) > .cap .side { color: color-mix(in srgb, var(--paper) 70%, var(--ink)); }
```

**Peek panel.** One panel of the reference column wakes up on the turn slide: it gets the accent, and on the last step another panel replaces it. The old panel stands for two screens. The new panel shows the call site of the fix. The accent is allowed here, because the speaker talks through this panel.

```css
.col.ref .peek .c-hit { color: var(--acc); font-weight: 700; }
.peek-main:not(.on) { display: none; }
.col.ref:has(.peek-main.on) .peek-ed { display: none; }
```

**Argument chips.** One row above the function head, inside the panel. A chip says what the caller passes into which parameter. Its border is the same 2px ink as the panels, with no fill. The row holds its height before the chips appear, so the code under it does not move. A chip drops in from above. Use one chip for each step. The value is the only accent.

```css
.args { display: flex; flex-wrap: wrap; gap: clamp(.5rem, 1.2vw, 1.2rem); min-height: 2.4em; padding: clamp(.5rem, 1.3vh, .9rem) clamp(.7rem, 1.4vw, 1.2rem) 0; font-family: var(--font-mono); font-size: clamp(.8rem, min(1.05vw, 1.8vh), 1.5rem); }
.arg { display: inline-flex; align-items: baseline; gap: .6em; border: 2px solid var(--ink); padding: .22em .7em; transform: translateY(-.3em); transition: opacity .3s ease .12s, transform .3s ease .12s; }
.arg.on { transform: none; }
.arg .to, .arg small { color: var(--mut); }
.arg small { font-size: .85em; }
.arg code { color: var(--acc); font-weight: 700; }
```

**Trigger marks.** On the first step, an accent underline falls on the lines that the speaker compares, and an accent box closes on the one value that explains the bug. The box has a transparent border from the start, so no character moves. The slide needs another `data-step="1"` element, such as an argument chip.

```css
.slide:not([data-shown="0"]) .ul { text-decoration: underline; text-decoration-color: var(--acc); text-decoration-thickness: .12em; text-underline-offset: .18em; }
.zero { padding: 0 .25em; border: 2px solid transparent; }
.slide:not([data-shown="0"]) .zero { border-color: var(--acc); color: var(--acc); font-weight: 700; }
```

**Mirror quiz.** Two equal panels ask one question about the same value in two places. The answers are `// ?` comments that swap to `.c-ans`. The panel with the surprise is the accent panel. The code is large, because the screen holds only these few lines. The audience gets five seconds. The next key shows the answers and the `.punch`, all on one step.

```css
.mirror { display: grid; grid-template-columns: 1fr 1fr; gap: clamp(.8rem, 2vw, 1.8rem); align-items: start; }
.mirror > * { min-width: 0; }
.mirror pre { font-size: clamp(1rem, min(1.55vw, 2.6vh), 2.3rem); line-height: 1.6; }
.mirror .c-com { color: var(--mut); }
```

```html
<h2 class="thesis">두 <b>sizeof</b> 는 각각 몇일까요?</h2>
<div class="mirror">
  <div class="panel">
    <div class="cap"><span>식에 놓인 배열</span><span class="side">main</span></div>
<pre>int <span class="c-hit">scores[5]</span>;
sizeof(scores);   <span class="swap"><span class="st-b c-com">// ?</span><span class="st-a c-ans" data-step="1">// 20</span></span></pre>
  </div>
  <div class="panel accent">
    <div class="cap"><span>인자로 들어간 배열</span><span class="side">show</span></div>
<pre>void show(<span class="swap"><span class="st-b c-hit">int arr[]</span><span class="st-a c-ans" data-step="1">int *arr</span></span>) {
    sizeof(arr);  <span class="swap"><span class="st-b c-com">// ?</span><span class="st-a c-ans" data-step="1">// 8</span></span>
}</pre>
  </div>
</div>
<p class="punch" data-step="1">함수 안에서는 arr 가 <b>포인터</b>로 들어옵니다.</p>
```

**Evidence trio.** The real debugger log is one tall accent panel at left. The two pieces of code that it proves are stacked at right. Lock the log with `data-evidence`. The caption side says that the log is real. A short muted word beside a value says what the value means. Dim the line that only sets the place.

```css
.panels.trio { grid-template-columns: 1fr 1fr; grid-template-rows: auto auto; }
.panels.trio .tall { grid-row: 1 / 3; }
.panels.trio pre { font-size: clamp(.9rem, min(1.2vw, 2.1vh), 1.9rem); line-height: 1.55; }
```

```html
<div class="panels trio">
  <div class="panel accent tall">
    <div class="cap"><span>gdb · bbSort 안에서</span><span class="side">실제 기록</span></div>
<pre data-evidence><span class="c-dim">Breakpoint 1, bbSort (arr=0x7fffffffc730, n=7)</span>

(gdb) p <span class="c-hit">ed(arr)</span>
$1 = <span class="c-hit">0</span>

(gdb) p sizeof(arr)
$2 = <span class="c-hit">8</span>      <span class="c-com">포인터</span></pre>
  </div>
  <div class="panel">...</div>
  <div class="panel">...</div>
</div>
```

**Reduced code label.** When the slide simplifies real code, the caption says so, and the original line range stays. Cut the tail of a function with a `.c-com` ellipsis.

```html
<div class="cap"><span>ed · 값으로 줄임</span><span class="side">4 – 9</span></div>
<pre>void bbSort(int arr []){
    for (int i = 0; i &lt; <span class="c-hit">ed(arr)</span>; i++){
        <span class="c-com">...</span></pre>
```

**Step dot.** A small breathing accent dot at the bottom edge tells the speaker that a step remains. It sits left of the stage home link. It goes away after the last step. Put `<div class="step-dot" aria-hidden="true"></div>` on each slide with steps.

```css
.step-dot { display: none; position: absolute; right: calc(var(--slide-padding) + 4vw); bottom: 0; z-index: 3; width: clamp(9px, .7vw, 14px); aspect-ratio: 1; border-radius: 50%; background: var(--acc); animation: breathe 1.9s ease-in-out infinite; }
.slide:has([data-step]:not(.on)) .step-dot { display: block; }
@keyframes breathe { 50% { opacity: .25; } }
```

**Four-beat head.** The left of `.head` names the beat of the story and the identifier under discussion. It shows the identifier as written, never in capitals.

```html
<div class="head"><span>起 · 내 len() 을 만들다</span><span class="num"></span></div>
<div class="head"><span>承 · copy1 이 태어나다</span><span class="num"></span></div>
<div class="head"><span>轉 · 둘이 만나 터지다</span><span class="num"></span></div>
<div class="head"><span>結 · ed 는 len 이 아니었다</span><span class="num"></span></div>
```

**Takeaway box.** One 2px ink box with a small accent label and two sentences. The accent is on the two words to keep.

```css
.takeaway { border: 2px solid var(--ink); padding: clamp(.8rem, 2vh, 1.4rem) clamp(.9rem, 1.8vw, 1.6rem); max-width: 58ch; font-size: clamp(1rem, 1.28vw, 1.85rem); line-height: 1.6; }
.takeaway b { color: var(--acc); }
.takeaway .k { display: block; font-family: var(--font-mono); font-size: var(--small-size); letter-spacing: .18em; text-transform: uppercase; color: var(--acc); margin-bottom: .5em; }
```

```html
<div class="takeaway"><span class="k">체크 항목</span>함수에 들어가는 순간 배열은 <b>포인터</b>가 됩니다.<br>정렬을 돌리려면 <b>길이를 인자로</b> 넣어야 합니다.</div>
```

## The turn slide

The turn slide uses most parts at once. Step 0 is the broken code, with `ed` in the reference. Step 1 adds the first chip, the underlines, the box on `0`, and the `.punch`. Step 2 adds the second chip, swaps the fix into the code, and replaces the peek panel with the call site.

```html
<h2 class="thesis">조용히 컴파일되고, 조용히 실행되고, <b>정렬은 안 되고</b></h2>
<div class="work">
  <div class="col src zoom-c">
    <div class="panel accent">
      <div class="cap"><span>sort.c · bbSort</span><span class="side">11 – 21</span></div>
      <div class="args" aria-hidden="true">
        <div class="arg" data-step="1">copy1 <small>(포인터로)</small><span class="to">→</span><code>int arr []</code></div>
        <div class="arg" data-step="2">ed(bb1)+1<span class="to">→</span><code>int n</code></div>
      </div>
<pre><span class="swap"><span class="st-b">void bbSort(int arr []){
    for (int i = 0; i &lt; <span class="c-hit">ed(arr)</span>; i++){</span><span class="st-a" data-step="2">void bbSort(int arr [], <span class="c-hit">int n</span>){
    for (int i = 0; i &lt; <span class="c-hit">n</span>; i++){</span></span>
        if (arr[i] &gt; arr[i+1]) swap(arr, i);
    }
}</pre>
    </div>
    <p class="punch" data-step="1">함수 안에서는 크기를 알 수 없음. <b>길이는 바깥에서 계산해 인자로</b> 넣어야 함.</p>
  </div>
  <div class="col ref">
    <div class="panel">
      <div class="cap"><span>cases.h</span><span class="side">INPUT</span></div>
<pre><span class="c-hit">const</span> int bb1[] = {64, 34, 25, 12};</pre>
    </div>
    <div class="panel accent peek peek-ed">
      <div class="cap"><span>ed · 값으로 줄임</span><span class="side">4 – 9</span></div>
<pre>int ed(const int arr []){
    return <span class="ul">(arr <span class="c-hit">== bb1</span>)</span> ? 6 :
                          <span class="zero">0</span>;
}</pre>
    </div>
    <div class="panel accent peek peek-main" data-step="2">
      <div class="cap"><span>sort.c · main</span><span class="side">33 – 37</span></div>
<pre>bbSort(copy1, <span class="c-hit">ed(bb1)+1</span>);  <span class="c-com">// 길이는 밖에서</span></pre>
    </div>
  </div>
</div>
<div class="step-dot" aria-hidden="true"></div>
```

## Do not

- Do not write any hex value in the deck. Use `var(--…)`, so that the student can change the accent.
- Do not draw a diagram. When a mechanism needs a picture, use another case.
- Do not highlight a whole line. Do not use `.hl` here. Mark the token.
- Do not use a dark code panel. The caption band is the only dark area. The log panel is light too.
- Do not use accent in the reference column, except on the peek panel.
- Do not put long text on the accent caption band. Paper on the accent is 3.67:1, under the 4.5:1 minimum for small text. Keep it to a file name and a line range.
- Do not paste a fake log. Text under `data-evidence` is real run output. A simplified code panel says so in its caption.
