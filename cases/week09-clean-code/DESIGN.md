---
version: alpha
name: Clean Code
description: Swiss white page with a light IDE panel. A wall of real code folds into function names, and the names become a tree and a table.
colors:
  canvas: "#ffffff"
  ink: "#0a0a0a"
  primary: "#ff3300"
  ink-mute: "#6b6b6b"
  surface: "#f7f7f5"
  hairline: "#ebebeb"
  code-fn: "#a63061"
  code-kw: "#9230a6"
  code-type: "#a65430"
  code-const: "#50384d"
  code-com: "#856aa0"
  code-var: "#61485e"
  code-guide: "#d87180"
typography:
  display: { fontFamily: IBM Plex Sans KR, fontWeight: 700, letterSpacing: -0.02em, lineHeight: 1.22 }
  body: { fontFamily: IBM Plex Sans KR, fontWeight: 400, lineHeight: 1.5 }
  mono: { fontFamily: IBM Plex Mono, fontWeight: 400, lineHeight: 1.55 }
---

# Clean Code

Use this style for a talk that argues about code structure from real code: a refactor, a naming rule, a module boundary.
Build on `templates/stage.html`. Do not change its runtime. Uncomment its IBM Plex `<link>` and font tokens. Map the six base colors with `reference/design.md` § Token mapping. The `code-*` keys are not in that mapping: set them with § Code theme.

The Swiss base is the same as `week07-circular-list`. This file covers what differs.

All SVG below follows `vendor/diagram-design/SKILL.md` § Slide-scale overrides. `SLOT` is the section id: `#SLOT` is the section, and `#SLOT-fig` is its figure. Replace it for each slide. The sample text comes from a talk on one syscall. Replace the names with the names in your own code.

ViewBox: code panel `0 0 1160 412`. Tree and table `0 0 1160 440`, with `max-height:66vh`.

## The one rule

**A function name gets the weight, and everything else recedes**. The audience must be able to follow the talk by reading the names only.

- In code, every function name has a marker. After the fold, each name is also bold.
- In the tree, a node holds a name and nothing else. In the table, each row starts from a name in a filled box.
- A filled ink box is on the path that the speaker walks. A white box is beside the path.
- The accent marks three things only: one phrase in a heading (`<em>`, or the second closing line), the spine that the speaker follows, and the place where the responsibility splits.
- The code hues stay in the code panel. Tree and table use ink, muted, and accent.

The accent is 3.67:1 on white and 3.42:1 on the panel. In a figure, accent text is weight 600 or more at size 19 or more.

## Slides

| Slide | Parts |
|---|---|
| Cover | `h1` with one `<em>`, `.ask` |
| Wall | `.thesis-row`, IDE panel with all code at size 12, no steps |
| Fold | Struck words, then `.thesis-row` and the IDE panel, which folds |
| Tree | Question to heading, then the camera figure |
| Table | `h2` with one `<em>`, the responsibility table |
| Close | two `.closing h1`, `.rule`, `.thanks` |

Usual order: as listed. The tree takes about a third of the talk. The thesis is `h2` at `--h2-size`, with one `<em>`. The figure fills the rest of the slide.
`.head`: the talk section and the slide's point on the left (`전환 · 책임 소재`). The number is on the right. `.foot`: the source files on the left, and the commit or the version on the right. The cover foot has the talk length on the right.

## CSS to add

Add this to the deck `<style>`. These rules are not in `stage.html`.
```css
#s1 h1 { max-width: none; }
.thesis-row { display: flex; justify-content: space-between; align-items: flex-end; gap: var(--content-gap); } .thesis-row h2 { max-width: none; }
```

The code theme: set one `:root` variable for each key. These hex values, with the base tokens, are the only hex values in the deck.

| Key | Variable | Use |
|---|---|---|
| `code-fn` | `--code-fn` | function names, gutter bars, signature band |
| `code-kw` | `--code-kw` | `if`, `while`, `return`, `struct` |
| `code-type` | `--code-type` | `void`, `size_t`, `int`, struct names |
| `code-const` | `--code-const` | `NULL`, `PGSIZE`, enum values |
| `code-com` | `--code-com` | comments. It is 4.29:1 on the panel: keep comments rare |
| `code-var` | `--code-var` | variables, operators, punctuation |
| `code-guide` | `--code-guide-base` | the base of `--code-guide` |

Two more variables derive from the keys.
```css
:root {
  --code-guide: color-mix(in srgb, var(--code-guide-base) 50%, var(--panel));
  --code-mark: color-mix(in srgb, var(--acc) 18%, var(--panel));
}
```

## Moves

**Struck words.** Start with no code. The common answer sits alone in the middle, large. Step 1 draws a line through it and shows the thesis. Step 2 replaces it with the panel. The overlay shares one grid cell, so the panel holds the space from the start. The padding keeps the strike inside its span, so the overflow notice of `stage.html` stays off. Keep the thesis to one line: at 1280×720 a two-line thesis overflows the panel.
```css
.overlay { display: grid; min-height: 0; } .overlay > * { grid-area: 1 / 1; }
.words { align-self: center; justify-self: center; font-weight: 700; font-size: clamp(1.8rem, 3.3vw, 5.2rem); letter-spacing: -.02em; white-space: nowrap; transition: color .4s ease; }
.words span { position: relative; display: inline-block; padding: 0 .1em; }
.words span::after { content: ""; position: absolute; left: 0; right: 0; top: 54%; height: .09em; background: var(--acc); transform: scaleX(0); transform-origin: left center; transition: transform .5s var(--ease); }
#SLOT:has(h2.on) .words { color: var(--mut); } #SLOT:has(h2.on) .words span::after { transform: scaleX(1); }
#SLOT:has(.after.on) .words { display: none; }
```
```html
<div class="thesis-row"><h2 data-step="1">진짜 맞추어야 하는 것은 <span data-step="2"><em>이런 느낌</em></span></h2></div>
<div class="overlay">
  <p class="words"><span>"동사 위치나 들여쓰기 같은 내용"</span></p>
  <figure id="SLOT-fig" class="panel" data-step="2">...</figure>
</div>
```
**Fold.** One step moves the 44-line wall into the 18-line read view. The wall holds for 1 second. Then each old line flies to the new line that replaced it, and fades. The read view fades in last. Use keyframes for the read view: the overflow check of `stage.html` turns off transitions on `[data-step]` while it measures.
```css
#SLOT:has(.after.on) .old { transform: translate(var(--dx), var(--dy)); opacity: 0; transition: transform .6s var(--ease) calc(1s + var(--d)), opacity .45s ease calc(1.15s + var(--d)); }
#SLOT:has(.after.on) .old-guides { opacity: 0; transition: opacity .3s ease 1s; }
#SLOT-fig .after.on { animation: fold-in .5s var(--ease) 1.45s backwards; }
@keyframes fold-in { from { opacity: 0; } to { opacity: 1; } }
body.edit-active #SLOT-fig, body.edit-active #SLOT-fig [data-step] { visibility: hidden !important; }
```

Wrap each wall line in one `.old` group. `--dx` is the new left margin minus the old one. `--dy` is the baseline of the new line that absorbs this line, minus the old baseline. A blank line has `0px` for both. `--d` is `0s`, `.08s`, or `.16s`, by block in reading order. Wall lines that became one call all have the same destination, and that convergence is the point.
```html
<g class="old-guides">...band, markers, guides of the wall...</g>
<g class="old" style="--dx:16px; --dy:64px; --d:0s"><text x="34" y="70" fill="var(--mut)" font-size="12" font-family="var(--font-mono)" text-anchor="end">4</text><text x="72.8" y="70" font-size="12" font-family="var(--font-mono)" style="white-space:pre"><tspan fill="var(--code-kw)">if</tspan><tspan fill="var(--code-var)"> (!</tspan><tspan fill="var(--code-fn)">is_valid_addr_and_length</tspan><tspan fill="var(--code-var)">(addr, length, offset)) {</tspan></text></g>
<g class="old" style="--dx:-552px; --dy:210px; --d:.08s"><text x="602" y="34" fill="var(--mut)" font-size="12" font-family="var(--font-mono)" text-anchor="end">24</text><text x="640.8" y="34" font-size="12" font-family="var(--font-mono)" style="white-space:pre"><tspan fill="var(--code-type)">void</tspan><tspan fill="var(--code-var)"> *va = addr;</tspan></text></g>
<g class="after" data-step="2">...read view...</g>
```
**Question to heading.** The question sits alone in the middle. Step 1 pushes it up, shrinks it, and mutes it, and the answer takes the middle. Step 2 lifts both away. The same answer is the `h2`, in its normal place, and the figure starts below it. The overlay is absolute, so `.slide-content` keeps its layout.
```css
.ask-over { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .4em; font-size: clamp(1.8rem, 3.3vw, 5.2rem); transition: opacity .25s ease, transform .4s var(--ease); }
.ask-over p { font-weight: 700; line-height: 1.3; letter-spacing: -.02em; white-space: nowrap; } .ask-over code { font-family: var(--font-mono); } .ask-over em { font-style: normal; color: var(--acc); }
.ask-over .q { transform: translateY(.85em); transition: transform .4s var(--ease), color .4s ease; }
#SLOT:has(.a.on) .ask-over { transform: translateY(-.85em); }
#SLOT:has(.a.on) .q { transform: scale(.72); color: var(--mut); }
#SLOT:has(h2.on) .ask-over { opacity: 0; visibility: hidden; transform: translateY(-2.4em); transition: opacity .25s ease, transform .4s var(--ease), visibility 0s linear .25s; }
body.jd-measure #SLOT .ask-over { display: none; }
body.edit-active #SLOT .ask-over { opacity: 1; visibility: visible; transform: none; }
```
```html
<div class="ask-over">
  <p class="q"><code>mmap()</code>은 무엇을 하는 함수인가?</p>
  <p class="a" data-step="1">"유저의 메모리 주소를 <em>파일 페이지에 매핑</em>해주기"</p>
</div>
<h2 data-step="2">"유저의 메모리 주소를 <em>파일 페이지에 매핑</em>해주기"</h2>
```
**Camera.** The tree is wider and taller than the viewBox. The viewBox is a window, and one `.cam` group slides under it, so the audience walks down the call tree. Step 2 is the chain across. Later steps move right and down. Set the x move to 580 minus the center x of the current node. Rank pitch is 148, so each move down is 148. Keep one window to 6 nodes or fewer.
```css
.cam { transform: translate(0, 148px); transition: transform .6s var(--ease); }
#SLOT-fig:has([data-step="3"].on) .cam { transform: translate(-280px, 0); }
#SLOT-fig:has([data-step="5"].on) .cam { transform: translate(-280px, -148px); }
body.edit-active #SLOT-fig, body.edit-active #SLOT-fig [data-step] { visibility: hidden !important; }
```
```html
<figure id="SLOT-fig">
<svg viewBox="0 0 1160 440" role="img" aria-label="..." style="width:100%; max-height:66vh; display:block">
<g class="cam">
  <g data-step="2">...chain...</g>
  <g data-step="3">...first rank...</g>
  <g data-step="4">...second rank...</g>
  <g data-step="5">...third rank...</g>
</g>
</svg>
</figure>
```
**Chain entrance.** The entry path enters from the left, one box at a time. When the camera turns down, the head of the chain fades, and the last box becomes the root of the tree.
```css
.chain-head { transition: opacity .3s ease; }
#SLOT-fig:has([data-step="3"].on) .chain-head { opacity: 0; }
#SLOT-fig g.on > .c1 { animation: chain-in .45s var(--ease) backwards; }
#SLOT-fig g.on > .c2 { animation: chain-in .45s var(--ease) .25s backwards; }
#SLOT-fig g.on > .c3 { animation: chain-in .45s var(--ease) .5s backwards; }
@keyframes chain-in { from { opacity: 0; transform: translateX(-24px); } to { opacity: 1; transform: none; } }
```
```html
<g class="chain-head c1"><rect x="200" y="16" width="160" height="72" fill="var(--ink)" stroke="var(--ink)" stroke-width="2"/><text x="280" y="59" fill="var(--paper)" font-size="20" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">mmap()</text></g>
<g class="c2"><line class="chain-head" x1="360" y1="52" x2="440" y2="52" stroke="var(--acc)" stroke-width="3"/><rect x="440" y="16" width="240" height="72" fill="var(--ink)" stroke="var(--ink)" stroke-width="2"/><text x="560" y="59" fill="var(--paper)" font-size="20" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">fd_to_file_mmap()</text></g>
<g class="c3"><line x1="680" y1="52" x2="760" y2="52" stroke="var(--acc)" stroke-width="3"/><rect x="760" y="16" width="200" height="72" fill="var(--ink)" stroke="var(--ink)" stroke-width="2"/><text x="860" y="59" fill="var(--paper)" font-size="20" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">do_mmap()</text></g>
```

## Figure vocabulary

Square corners on every box. No shadow, no gradient, no icon, no arrowhead. Height and position carry the direction. The only curve is the small elbow on a tree branch.

### Code panel

Draw in this order: band, markers, guides, text. Mono advance is .6em, so every position comes from a character grid. Compute the positions. Do not place them by eye.

**IDE panel.** A light `.panel` with a breadcrumb in the caption. Put `data-evidence` on real code. The code is from `git show`, unchanged, even where a line looks odd.
```html
<figure id="SLOT-fig" class="panel" data-evidence>
  <div class="cap"><span>vm › file.c › do_mmap()</span><span>before</span></div>
  <svg viewBox="0 0 1160 412" role="img" aria-label="리팩토링 전 do_mmap() 44줄 전체." style="width:100%; max-height:70vh; display:block">...</svg>
</figure>
```
**Wall line.** Size 12, pitch 18, first baseline 16. A character is 7.2 wide, and one indent is 28.8. Two columns: number at x 34 and code at x 44, then number at x 602 and code at x 612. The wall does not ask to be read. Its density is the argument, and the speaker says so. Use size 12 only here. Use `--code-var` for all text that has no other role.
```html
<text x="34" y="70" fill="var(--mut)" font-size="12" font-family="var(--font-mono)" text-anchor="end">4</text>
<text x="72.8" y="70" font-size="12" font-family="var(--font-mono)" style="white-space:pre"><tspan fill="var(--code-kw)">if</tspan><tspan fill="var(--code-var)"> (!</tspan><tspan fill="var(--code-fn)">is_valid_addr_and_length</tspan><tspan fill="var(--code-var)">(addr, length, offset)) {</tspan></text>
```
**Read line.** Size 17, pitch 22, first baseline 24, one column. A character is 10.2 wide, and one indent is 40.8. The number is size 14 at x 40, and code starts at x 60. Each function name is weight 700.
```html
<text x="100.8" y="134" font-size="17" font-family="var(--font-mono)" style="white-space:pre"><tspan fill="var(--code-kw)">if</tspan><tspan fill="var(--code-var)"> (!</tspan><tspan fill="var(--code-fn)" font-weight="700">is_valid_addr_and_length</tspan><tspan fill="var(--code-var)">(addr, length)) {</tspan></text>
```
**Indent guide.** One short vertical line per indent level on each code line. Blank lines keep their guides, so the block stays unbroken. The line runs from baseline minus 13 to baseline plus 5 on the wall, and minus 16 to plus 6 in the read view.
```html
<line x1="44" y1="57" x2="44" y2="75" stroke="var(--code-guide)" stroke-width="1"/>
```
**Name marker.** A tint behind every function name, like a search hit in an editor. On the wall: x = text x + 7.2 × offset − 1, y = baseline − 9.8, width = 7.2 × length + 2, height 13. In the read view: x = text x + 10.2 × offset − 1, y = baseline − 13.9, width = 10.2 × length + 2, height 18.4.
```html
<g class="fn-marks"><rect x="107.8" y="60.2" width="174.8" height="13" fill="var(--code-mark)"/></g>
```
**Signature band.** A wash across the signature lines of the function under discussion. It spans one column on the wall and the full width in the read view.
```html
<rect x="0" y="3" width="578" height="36" fill="color-mix(in srgb, var(--code-fn) 10%, var(--panel))"/>
```
**Gutter bar.** In the read view only. A bar between the number and the code marks each block of the new function: before, core, after. The eye sees three parts before it reads a word.
```html
<rect x="46" y="118" width="4" height="86" fill="var(--code-fn)"/>
```

### Name tree

**Tree node.** A name in a box, height 72, width 12 × name length + 28 or more. Baseline is y + 43. Rank pitch is 148: a node of 72 and a gap of 76. A function on the speaker's path has ink fill and paper text. A function beside the path has white fill and ink text.
```html
<rect x="740" y="164" width="240" height="72" fill="var(--ink)" stroke="var(--ink)" stroke-width="2"/>
<text x="860" y="207" fill="var(--paper)" font-size="20" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">alloc_file_page()</text>
<rect x="1160" y="164" width="240" height="72" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
<text x="1280" y="207" fill="var(--ink)" font-size="20" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">record_page_cnt()</text>
```
**Spine and branches.** The spine goes straight down in accent, stroke 3. Branches leave it 38 below the parent node, in muted, stroke 2, with an elbow of radius 8. Draw the branches first, so that the spine lies on top. When the talk follows a side child, draw that one branch in accent, stroke 3, and draw the straight line muted.
```html
<path d="M860,126 H468 Q460,126 460,134 V164" fill="none" stroke="var(--mut)" stroke-width="2"/>
<path d="M860,126 H1272 Q1280,126 1280,134 V164" fill="none" stroke="var(--mut)" stroke-width="2"/>
<line x1="860" y1="88" x2="860" y2="164" stroke="var(--acc)" stroke-width="3"/>
```
**Branch label.** The role of a child, in Korean body bold, just above it and 10 over its top edge. The label starts near the branch line. The core child has the accent label. A loop is one muted keyword beside the spine, not a shape.
```html
<text x="472" y="154" fill="var(--ink)" font-size="18" font-weight="700" font-family="var(--font-body)">전처리 (validation check)</text>
<text x="872" y="154" fill="var(--acc)" font-size="19" font-weight="700" font-family="var(--font-body)">핵심 로직</text>
<text x="846" y="280" fill="var(--mut)" font-size="16" font-family="var(--font-mono)" text-anchor="end">while</text>
```
**Check stack.** Sibling checks that do one job share one white box. Weight 500, size 18, pitch 34.
```html
<rect x="300" y="164" width="320" height="112" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
<text x="460" y="196" fill="var(--ink)" font-size="18" font-weight="500" font-family="var(--font-mono)" text-anchor="middle">is_valid_addr_and_length()</text>
<text x="460" y="230" fill="var(--ink)" font-size="18" font-weight="500" font-family="var(--font-mono)" text-anchor="middle">is_valid_offset()</text>
<text x="460" y="264" fill="var(--ink)" font-size="18" font-weight="500" font-family="var(--font-mono)" text-anchor="middle">is_page_range_unused()</text>
```
**Group bracket.** Under the last rank, a square bracket names what its children have in common. Two brackets split the rank into two concerns.
```html
<path d="M300,538 V546 H964 V538" fill="none" stroke="var(--mut)" stroke-width="2"/>
<text x="632" y="570" fill="var(--ink)" font-size="18" font-weight="700" font-family="var(--font-body)" text-anchor="middle">파일 관련 부분</text>
```

### Responsibility table

An SVG table, not an HTML one, so that lines can cross the columns. Columns start at x 20 (layer), 150 (function), 510 (responsibility), and 850 (data). Column headers are body bold, size 18, at y 24. Rows are 44 high with pitch 66, from y 40. Use 6 rows or fewer.

**Function row.** A filled box, a short connector to the next box, a one-line job, and a thin rule between rows. Each identifier in the job is mono, weight 600.
```html
<line x1="320" y1="150" x2="320" y2="172" stroke="var(--mut)" stroke-width="2"/>
<line x1="510" y1="161" x2="1140" y2="161" stroke="color-mix(in srgb, var(--ink) 18%, var(--paper))" stroke-width="1"/>
<rect x="150" y="106" width="340" height="44" fill="var(--ink)" stroke="var(--ink)" stroke-width="2"/>
<text x="320" y="134" fill="var(--paper)" font-size="17" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">fd_to_file_mmap()</text>
<text x="510" y="133" fill="var(--ink)" font-size="16" font-weight="500" font-family="var(--font-body)"><tspan font-family="var(--font-mono)" font-weight="600">fd</tspan><tspan>를 </tspan><tspan font-family="var(--font-mono)" font-weight="600">file</tspan><tspan>로 바꾸기</tspan></text>
```
**Layer cell.** One muted box spans the rows of one layer, so that the table shows where each function lives.
```html
<rect x="20" y="172" width="110" height="242" fill="var(--paper)" stroke="var(--mut)" stroke-width="2"/>
<text x="75" y="299" fill="var(--ink)" font-size="17" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">vm</text>
```
**Late column.** The data column arrives on a step, after the header, one cell after another. An inline delay staggers the cells. Each cell lines up with its function.
```html
<g data-step="1"><text x="850" y="24" fill="var(--ink)" font-size="18" font-weight="700" font-family="var(--font-body)">구조체</text></g>
<g data-step="1" style="transition-delay:.15s"><rect x="850" y="106" width="290" height="44" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/><text x="995" y="133.6" fill="var(--ink)" font-size="16" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">int fd <tspan fill="var(--acc)">→</tspan> struct file</text></g>
```
**Split line.** The last step draws one accent line over a row rule, across every column from the function column on. A paper plate under the label cuts the line. This is the claim of the slide, so it has the only accent line.
```html
<g data-step="2">
  <line x1="150" y1="293" x2="1140" y2="293" stroke="var(--acc)" stroke-width="2"/>
  <rect x="560" y="281" width="280" height="24" fill="var(--paper)"/>
  <text x="700" y="300" fill="var(--acc)" font-size="19" font-weight="700" font-family="var(--font-body)" text-anchor="middle">"파일"과 "페이지"로 갈라짐</text>
</g>
```
**Split cell.** Each side of the split gets an accent-outlined data cell on `--hl`, with its name in accent on the left.
```html
<g data-step="2" style="transition-delay:.25s">
  <text x="775" y="332" fill="var(--acc)" font-size="19" font-weight="700" font-family="var(--font-body)">파일</text>
  <rect x="850" y="304" width="290" height="44" fill="var(--hl)" stroke="var(--acc)" stroke-width="2"/>
  <text x="995" y="331.6" fill="var(--ink)" font-size="16" font-weight="600" font-family="var(--font-mono)" text-anchor="middle">struct load_info</text>
</g>
```

## Do not

- Do not write a hex value outside `:root`. Use `var(--…)`, so that the student can change the theme.
- Do not use a code hue outside the code panel, and do not use a dark panel. The code stays on the light `--panel`.
- Do not mark some function names and skip others. A partial marker reads as a claim about those names.
- Do not rewrite or tidy the code on the wall. Real code is the evidence.
- Do not set the read view below size 17. Size 12 is for the wall only, which the audience is not asked to read.
- Do not put a description in a tree node. A node is a name. The speaker says the rest.
- Do not fit a figure by shrinking text. Split the slide (`reference/build.md`, density limits).
