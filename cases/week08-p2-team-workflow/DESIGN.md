---
version: alpha
name: Team Workflow
description: Swiss white page. One whiteboard map holds the talk, one region lit at each stop. Real screenshots prove each stop. One color per person.
colors:
  canvas: "#ffffff"
  ink: "#0a0a0a"
  primary: "#ff3300"
  ink-mute: "#6b6b6b"
  surface: "#f7f7f5"
  hairline: "#ebebeb"
  person-b: "#0e7c6b"
  person-c: "#2f5bd3"
  shared: "#9a9a9a"
  warn: "#d9a400"
typography:
  display: { fontFamily: IBM Plex Sans KR, fontWeight: 700, letterSpacing: -0.02em, lineHeight: 1.34 }
  body: { fontFamily: IBM Plex Sans KR, fontWeight: 400, lineHeight: 1.45 }
  mono: { fontFamily: IBM Plex Mono, fontWeight: 400, lineHeight: 1.55 }
---

# Team Workflow

Use this style for a talk about a process over time: a team's week, a migration, a release. It fits a talk that has real screenshots as evidence.
Build on `templates/stage.html`. Do not change its runtime. Uncomment its IBM Plex `<link>` and font tokens. Map the base colors with `reference/design.md` § Token mapping. Set `--p-b`, `--p-c`, `--p-all`, and `--warn` in `:root` from `person-b`, `person-c`, `shared`, and `warn` above.

The base is the same Swiss page as `cases/week07-circular-list`: 12-column grid, head and foot bands, one accent. The map, the screenshots, and the person colors are what is new here.

All SVG follows `vendor/diagram-design/SKILL.md` § Slide-scale overrides. `SLOT` is the slot id. Coordinates are examples. Keep the font sizes and stroke widths, and re-space the shapes. The original drew at 1600 wide. This file uses a full-width viewBox of `0 0 1160 470`, so that the text stays readable.

## The one rule

**One map, one lit region**: the same map returns before each section. Only the next region is at full strength. Evidence follows it.

- The map never moves. Every stop has the same shapes at the same coordinates. The audience tracks a region by its place.
- The map shows the plan. The next slide shows what really happened, as a real screenshot or a figure from real data.
- Accent in the map is only on the arrows that change state. Accent in a heading is the name of the lit region.
- A person keeps one color on every slide. Person A is the accent, so that person's figure text is weight 600 at size 19 or more.
- Every image is a screenshot from the team's real tools. This deck shows no photo.

## Slides

| Slide | Parts |
|---|---|
| Cover | `.kicker`, `h1` with one `<em>`, `.ask`, `.punch` with the three tools in `<b>` |
| Map, built | `h2`, Whiteboard map with 4 steps |
| Map stop | `h2` as `<em>region</em> → next`, Map stop, no step, 3 seconds |
| Two shots | `h2`, Framed shot twice in `.two.even`, `.punch` |
| Assignment | `h2`, Crop rows |
| Replay | `h2`, `.replay`: Shot then replay on step 1, Person chip rows beside it on step 2 |
| History | `h2`, Branch graph |
| Zones | `h2`, Zone cards, Scope bracket |
| Marked shot | `h2` as one full sentence, Marked shot and Status track on one step |
| Close | `.kicker`, `h1`, second `h1` on step 1, `.punch` and `.thanks` on step 2 |

Usual order: cover, map built, then stop and evidence by turns, close. Each stop has the next section's date or name at the right of its `.foot`.
`.head`: the date or the span of this section on the left. The number is on the right. A stop's `.head` is `지도 · 다음`. `.foot`: the source file, tool, or branch behind the slide.
The `h2` states the point. The figure or the screenshot is the slide.

## CSS to add

Add this to the deck `<style>`. These classes are not in `stage.html`. Each part below adds its own CSS.

```css
:root { --p-a: var(--acc); } h1 { line-height: 1.34; padding-bottom: .1em; } h2 { line-height: 1.42; padding-bottom: .1em; } .closing h1 { font-size: clamp(1.4rem, 2.3vw, 3.6rem); max-width: 40ch; line-height: 1.42; }
.two { display: grid; grid-template-columns: 1.15fr 1fr; gap: clamp(.8rem, 2vw, 2rem); align-items: start; min-height: 0; } .two.even { grid-template-columns: 1fr 1fr; } .board { margin: 0; min-height: 0; color: var(--ink); }
.board svg { font-family: var(--font-body); display: block; width: 100%; height: auto; max-height: 66vh; } .board figcaption { font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); margin-top: .4em; } .who { font-family: var(--font-mono); font-size: var(--small-size); font-weight: 600; white-space: nowrap; }
.who::before { content: ''; display: inline-block; width: .7em; height: .7em; margin-right: .35em; background: var(--c); vertical-align: -.05em; } .who.a { --c: var(--p-a); } .who.b { --c: var(--p-b); } .who.c { --c: var(--p-c); } .who.all { --c: var(--p-all); }
```

**Person chip.** A small square in the person's color and the name in mono. Use it at the left of a row, in a block's owner line, and in a key under a board. `--c` also colors board cells and row bars. Gray means the code of several people.
```html
<span class="who b">멤버 B</span><div class="who all" style="grid-column:1/-1">회색 = 여러 사람 코드가 함께 필요한 테스트</div>
```

## The map

Draw the map once. It is a whiteboard redrawn: the shapes are loose and the labels are bold.

**Whiteboard map.** One SVG inside `figure.board`. The root sets `fill="none"` and `stroke="currentColor"`, so that a shape needs no paint and a text group sets `fill` and `stroke="none"`. A concept is an ellipse. A thing or a place is a box with `rx="4"`. Each region is one `<g class="rg">`. On the first map slide, step groups wrap the regions.
```html
<figure class="board"><svg viewBox="0 0 1160 470" role="img" aria-label="..." fill="none" stroke="currentColor" stroke-width="2.5">
  <defs><marker id="SLOT-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="var(--ink)" stroke="none"/></marker><marker id="SLOT-ah-acc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="var(--acc)" stroke="none"/></marker></defs>
  <g data-step="1">
    <g class="rg">
      <rect x="30" y="70" width="100" height="44" rx="4"/><rect x="30" y="130" width="100" height="44" rx="4"/><ellipse cx="250" cy="122" rx="56" ry="30"/>
      <path d="M138 74 Q155 74 155 88 L155 108 Q155 122 166 122 Q155 122 155 136 L155 156 Q155 170 138 170"/><line x1="170" y1="122" x2="192" y2="122" marker-end="url(#SLOT-ah)"/>
      <g fill="var(--ink)" stroke="none" font-size="22" font-weight="700" text-anchor="middle"><text x="80" y="100">회의</text><text x="80" y="160">PR</text><text x="250" y="130">작업</text></g>
      <text x="250" y="172" fill="var(--mut)" stroke="none" font-size="16" text-anchor="middle">단위를 정한다</text>
    </g>
    <g class="rg"><ellipse cx="440" cy="62" rx="54" ry="30"/><text x="440" y="70" fill="var(--ink)" stroke="none" font-size="22" font-weight="700" text-anchor="middle">공통</text></g>
    <g class="rg"><ellipse cx="440" cy="212" rx="54" ry="30"/><text x="440" y="220" fill="var(--ink)" stroke="none" font-size="22" font-weight="700" text-anchor="middle">분할</text></g>
  </g>
</svg></figure>
```

**Two-way arrows.** Two states that swap get one arrow each way, side by side, in accent. A bold accent label names the direction, and an ink line gives the condition. These are the only accent lines on the map.
```html
<g class="rg"><line x1="468" y1="90" x2="468" y2="178" stroke="var(--acc)" marker-end="url(#SLOT-ah-acc)"/>
  <g fill="var(--ink)" stroke="none" font-size="16"><text x="500" y="110" font-size="19" font-weight="700" fill="var(--acc)">↓ 공통 → 분할</text><text x="500" y="134">시간이 부족하면</text></g></g>
<g class="rg"><line x1="412" y1="184" x2="412" y2="96" stroke="var(--acc)" marker-end="url(#SLOT-ah-acc)"/></g>
```

**Map card.** A region that holds a list is a large box on `--panel`, with a bold title, numbered lines, a muted thin rule, and one mono line for the key item. A later link is dashed and has a muted label.
```html
<g class="rg"><line x1="494" y1="62" x2="720" y2="62" marker-end="url(#SLOT-ah)"/>
  <rect x="724" y="24" width="410" height="240" rx="4" fill="var(--panel)"/>
  <g fill="var(--ink)" stroke="none" font-size="18"><text x="746" y="62" font-size="22" font-weight="700">첫날 할 일</text><text x="746" y="100">1  문서 읽기</text><text x="746" y="136">2  도는 방식 조사</text></g>
  <line x1="746" y1="186" x2="1112" y2="186" stroke="var(--mut)" stroke-width="1.5"/>
  <text x="746" y="226" fill="var(--ink)" stroke="none" font-family="var(--font-mono)" font-size="20" font-weight="700">★ fork() wait()</text></g>
<g class="rg"><line x1="494" y1="212" x2="720" y2="212" stroke-dasharray="9 7" marker-end="url(#SLOT-ah)"/><text x="606" y="240" fill="var(--mut)" stroke="none" font-size="16" text-anchor="middle">핵심 기능 이후</text></g>
```

**Map stop.** Copy the map as it is, with no step groups. Give the lit regions `hi`. A stop may light two regions: an arrow and the state it reaches. A dim region carries no meaning on this slide, because the audience saw it at full strength on the first map. The stop's `h2` names the region. The original generated all stops by script from the first map, so that they cannot drift. Each stop needs its own marker ids.
```css
.mapslide .rg { opacity: .14; } .mapslide .rg.hi { opacity: 1; }
```
```html
<section class="slide mapslide" id="SLOT"><div class="head"><span>지도 · 다음</span><span class="num"></span></div>
  <div class="slide-content"><h2><em>분할</em> → 기능 단위로 다시 나누기</h2><figure class="board"><svg viewBox="0 0 1160 470" role="img" aria-label="..." fill="none" stroke="currentColor" stroke-width="2.5"><g class="rg">...</g><g class="rg hi">...</g></svg></figure></div>
  <div class="foot"><span>첫날 칠판 지도</span><span>토 · 10.17</span></div><aside class="notes" data-sec="3"><p>다음은 분할입니다.</p></aside></section>
```

## Screenshots

All eight images in the original are PNG crops of a browser page or an editor. Crop each file to the block: remove the browser frame and the page around the block, and keep the small page margin. Crops that sit together come from one page at one zoom, with about the same width. Their heights can differ. The `alt` holds the content of the screenshot, in one sentence. The caption or column head says what the crop is. It does not explain it. Only one image has marks, and they are in the file. No SVG or CSS mark sits on top of an image.

**Framed shot.** The default frame: an ink border on paper, a contained image, and a mono caption under a thin rule. Two near-square shots sit side by side, with one `.punch` under them. There is no step: the whole page is one piece of evidence.
```css
.shot { border: 2px solid var(--ink); background: var(--paper); min-width: 0; } .shot img { display: block; width: 100%; max-height: 52vh; object-fit: contain; } .shot.tall img { max-height: 60vh; } .shot figcaption { font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); padding: .35em .8em; border-top: 1.5px solid var(--cap-b); }
```
```html
<div class="two even">
  <figure class="shot tall"><img src="deck.assets/quiz-1.png" alt="쪽지 시험 1·2번: ..."><figcaption>1 · 2번</figcaption></figure>
  <figure class="shot tall"><img src="deck.assets/quiz-2.png" alt="쪽지 시험 3·4번: ..."><figcaption>3 · 4번</figcaption></figure>
</div>
<p class="punch">오후 강의를 <b>듣기 위한 사전 준비</b></p>
```

**Crop rows.** Compare the plan with the result, one person per row. On the left is a thin crop of that person's block from the plan page, with no frame, because the crop has its own card border. On the right is what the person really did, behind a thick bar in the person's color. The crop and its text share one step. Pin each crop to the left, so that crops of different heights keep one left edge.
```css
.assign { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr); gap: clamp(.5rem, 1.4vh, 1.1rem) clamp(.8rem, 2vw, 2rem); align-items: center; } .assign .colh { font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); border-bottom: 1.5px solid var(--cap-b); padding-bottom: .25em; }
.assign img { display: block; width: 100%; max-height: 17vh; object-fit: contain; object-position: left center; } .assign .did { border-left: 6px solid var(--c); padding: .3em 0 .3em .9em; font-size: var(--body-size); line-height: 1.45; } .assign .did .who { display: block; margin-bottom: .15em; }
.assign .did code { font-family: var(--font-mono); font-size: .9em; } .assign .did.a { --c: var(--p-a); } .assign .did.b { --c: var(--p-b); } .assign .did.c { --c: var(--p-c); }
```
```html
<div class="assign">
  <div class="colh">계획표 · 화요일에 나눈 일</div><div class="colh">실제로 짠 것 · 커밋 기록</div>
  <img data-step="1" src="deck.assets/block-a.png" alt="화요일 블록: 실패 정리, 멤버 A, 13/13">
  <div class="did a" data-step="1"><span class="who a">멤버 A (나)</span><code>page_fault()</code> 수정 · 작은 기능 둘 · 테스트 하나 추가</div>
  <img data-step="2" src="deck.assets/block-b.png" alt="화요일 블록: 복제, 멤버 B, 4/4">
  <div class="did b" data-step="2"><span class="who b">멤버 B</span>표 구조부터 만들고 나머지 기능까지</div>
</div>
```

**Shot then replay.** The real page comes first, then it crossfades into a rebuilt copy that plays its own history. Both layers share one grid cell, so the swap moves nothing. The top image of the real layer is a thin strip with the rule of the page. The lower image takes the remaining height. The rebuilt copy has `data-evidence`, so that edit mode leaves it alone. The caption says which layer is on screen. The replay needs the data of the real run. Do not make up the numbers.
```css
.replay { display: grid; grid-template-columns: 1.25fr 1fr; gap: clamp(.8rem, 2vw, 2rem); align-items: start; min-height: 0; } .pstage { display: grid; min-width: 0; } .pstage > * { grid-area: 1 / 1; min-width: 0; transition: opacity .6s var(--ease); }
.preal { display: flex; flex-direction: column; gap: .4em; align-items: center; justify-content: center; border: 2px solid var(--ink); background: var(--paper); padding: clamp(.4rem, 1.1vh, .9rem); opacity: 0; pointer-events: none; min-height: 0; overflow: hidden; }
.preal img { display: block; max-width: 100%; min-height: 0; object-fit: contain; } .preal img:last-child { flex: 1; max-height: 44vh; } .pstage.real .preal { opacity: 1; } .pstage.real .pboard { opacity: 0; } .pstage.real + .ptotal > span:last-child { visibility: hidden; }
.ptotal { display: flex; justify-content: space-between; align-items: baseline; font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); padding-top: .35em; } .ptotal b { font-size: var(--h3-size); color: var(--ink); }
```
```html
<figure class="board" data-step="1">
  <div class="pstage real" id="SLOT-stage">
    <div class="pboard" id="SLOT-board" title="눌러서 다시 재생" data-evidence></div>
    <div class="preal" data-evidence><img src="deck.assets/page-rule.png" alt="..."><img src="deck.assets/page-board.png" alt="..."></div>
  </div>
  <div class="ptotal"><span id="SLOT-cap"></span><span><b id="SLOT-done">0</b> / <span id="SLOT-all">0</span></span></div>
</figure>
```

**Test board.** The rebuilt copy: one block per task, with the day tag, the title, the count, the owners, a thin bar, and one square per test. A square fills in the color of the person whose code passes that test. A test in two blocks fills both at one moment. Build it in JS from the real data. The real layer holds for 6 seconds. `→` during that time skips to the replay, and a click replays it.
```css
.pboard { border: 2px solid var(--ink); background: var(--paper); padding: clamp(.4rem, 1.1vh, .9rem); display: grid; grid-template-columns: 1fr 1fr; gap: clamp(.3rem, .9vh, .7rem); cursor: pointer; min-width: 0; }
.pblock { border: 1.5px solid var(--cap-b); padding: .35em .5em .45em; min-width: 0; } .pblock .bh { display: flex; align-items: baseline; gap: .45em; font-size: var(--small-size); line-height: 1.3; } .pblock .bh b { font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.pblock .bh .d { font-family: var(--font-mono); color: var(--mut); border: 1px solid var(--cap-b); padding: 0 .3em; flex: none; } .pblock .bh .n { margin-left: auto; font-family: var(--font-mono); color: var(--mut); flex: none; }
.pblock .owners { display: flex; gap: .7em; margin: .15em 0 .25em; } .pblock .bar { height: 4px; background: color-mix(in srgb, var(--ink) 10%, transparent); margin-bottom: .35em; } .pblock .bar i { display: block; height: 100%; width: 0; background: var(--ink); transition: width .25s linear; } .pblock .cells { display: flex; flex-wrap: wrap; gap: 3px; }
.pblock .cells span { width: clamp(11px, 1.3vw, 26px); aspect-ratio: 1; border: 1.5px solid color-mix(in srgb, var(--ink) 35%, transparent); background: var(--paper); transition: background-color .2s, border-color .2s, transform .2s var(--ease); } .pblock .cells span.on { background: var(--c); border-color: var(--c); transform: scale(1.08); } .pblock .cells span.on.settled { transform: none; }
```
```js
(() => {
  const WHO = { a: 't1 t2', b: 't3 t4' }, NAMES = { a: '멤버 A', b: '멤버 B', all: '전원' };   // a test not listed is gray
  const BLOCKS = [['월', '기능 1', ['a'], 't1 t2 t3'], ['화', '기능 2', ['b'], 't3 t4 t5']];   // day, title, owners, tests
  const $ = s => document.getElementById('SLOT-' + s), board = $('board'), stage = $('stage'), cap = $('cap'), done = $('done');
  const fig = board.closest('[data-step]'), who = {}, cells = []; let timers = [], realT = 0;
  Object.entries(WHO).forEach(([k, v]) => v.split(' ').forEach(t => who[t] = k));
  board.replaceChildren();   // a restored draft can carry the blocks of an earlier run
  const blocks = BLOCKS.map(([day, title, owners, tests]) => {
    const el = document.createElement('div'), ts = tests.split(' '); el.className = 'pblock'; el.innerHTML = `<div class="bh"><span class="d">${day}</span><b>${title}</b><span class="n">0 / ${ts.length}</span></div><div class="owners">${owners.map(o => `<span class="who ${o}">${NAMES[o]}</span>`).join('')}</div><div class="bar"><i></i></div><div class="cells"></div>`; const b = { n: el.querySelector('.n'), bar: el.querySelector('.bar i'), total: ts.length, done: 0 }; ts.forEach(t => { const c = document.createElement('span'); c.style.setProperty('--c', `var(--p-${who[t] || 'all'})`); el.querySelector('.cells').appendChild(c); cells.push({ c, b, t }); }); board.appendChild(el); return b; }); $('all').textContent = cells.length;
  const paint = b => { b.n.textContent = `${b.done} / ${b.total}`; b.bar.style.width = 100 * b.done / b.total + '%'; };
  const reset = () => { timers.forEach(clearTimeout); timers = []; cells.forEach(x => x.c.classList.remove('on', 'settled')); blocks.forEach(b => { b.done = 0; paint(b); }); done.textContent = 0; };
  function play() { reset(); const instant = matchMedia('(prefers-reduced-motion: reduce)').matches, at = {}; let n = 0; [...new Set(cells.map(x => x.t))].sort(() => Math.random() - .5).forEach((t, i, all) => at[t] = instant ? 0 : 400 + i * 5200 / all.length + Math.random() * 120); cells.forEach(x => timers.push(setTimeout(() => { x.c.classList.add('on'); timers.push(setTimeout(() => x.c.classList.add('settled'), 220)); x.b.done++; paint(x.b); done.textContent = ++n; }, at[x.t]))); }
  const toReplay = () => { clearTimeout(realT); realT = 0; stage.classList.remove('real'); cap.textContent = '재현: 테스트 한 번 · 칸 색 = 코드를 짠 사람'; play(); }; const toReal = wait => { reset(); stage.classList.add('real'); cap.textContent = '실제 화면'; clearTimeout(realT); realT = wait ? setTimeout(toReplay, 6000) : 0; };
  new MutationObserver(() => { if (!fig.classList.contains('on')) toReal(false); else if (!realT && !timers.length) toReal(true); }).observe(fig, { attributes: true, attributeFilter: ['class'] }); window.addEventListener('keydown', e => { if (realT && fig.classList.contains('on') && ['ArrowRight', ' ', 'PageDown'].includes(e.key)) { e.preventDefault(); e.stopImmediatePropagation(); toReplay(); } }, true); board.addEventListener('click', toReplay); cap.textContent = '실제 화면';
})();
```

**Marked shot.** One dark editor screenshot, unframed, at up to 56vh, pinned left, with a mono caption. It is the only dark area in the deck, so it draws the eye. Draw the marks into the image file before you add it: a thick solid red rectangle around each spot, with square corners, no number, no arrow, and no label. Choose a red close to the accent.
```css
.drill { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: clamp(.8rem, 2vw, 2rem); align-items: center; } .drill img { display: block; width: 100%; max-height: 56vh; object-fit: contain; object-position: left center; } .drill figcaption { font-family: var(--font-mono); font-size: var(--small-size); color: var(--mut); margin-top: .3em; }
```

**Status track.** The rows beside the marked shot. Each row has a mono number, a mono status word, and the item. Only the half-done row is accent. Rows not reached are muted. The caption line above gives the time box. The whole `.drill` is one step.
```css
.track { list-style: none; margin: 0; padding: 0; display: grid; gap: clamp(.25rem, .8vh, .6rem); } .track li { display: grid; grid-template-columns: 1.4em 5em 1fr; align-items: baseline; gap: .6em; font-size: var(--body-size); }
.track .n { font-family: var(--font-mono); color: var(--mut); } .track .s { font-family: var(--font-mono); font-size: var(--small-size); font-weight: 600; } .track .half .s { color: var(--acc); } .track .none { color: var(--mut); } .track .none .s { font-weight: 500; } .track code { font-family: var(--font-mono); font-size: .92em; }
```
```html
<div class="drill" data-step="1"><figure><img src="deck.assets/blanks.png" alt="코드에 빈칸을 뚫어 둔 화면: ..."><figcaption><code>handler</code>를 빈칸으로 뚫고 다시 채우기</figcaption></figure>
  <div><div class="cap"><span>화요일 밤 · 6시간</span></div><ol class="track" data-evidence><li class="done"><span class="n">1</span><span class="s">완료</span><span><code>exec</code></span></li><li class="half"><span class="n">2</span><span class="s">중간까지</span><span><code>fork</code></span></li><li class="none"><span class="n">3</span><span class="s">못 함</span><span>그 뒤 기능</span></li></ol></div></div>
```

## Figure vocabulary

Text in a figure is `--font-body`. Identifiers, branch names, and values are mono. Corners are small, not zero: `rx="4"` on a box, full pills on a graph. No shadow, no gradient, no icon.

**Branch graph.** A person is one track, in that person's color. The shared branch is in the middle at stroke 5, and the main branch is at the top at 2.5. Day lines are in `--grid`, with mono day names at the top. Everyone starts from one dashed line down from the base commit. The original ran 7 steps in a longer talk. Hold 4: keep only the merges that the speaker names.
```html
<g stroke-width="1" stroke="var(--grid)"><line x1="290" y1="14" x2="290" y2="400"/></g><text x="296" y="24" font-family="var(--font-mono)" font-size="14" fill="var(--mut)" stroke="none">토 10.17</text><line x1="120" y1="44" x2="1150" y2="44" stroke="var(--ink)" stroke-width="2.5"/><text x="12" y="49" font-family="var(--font-mono)" font-size="16" font-weight="600" fill="var(--ink)" stroke="none">main</text>
<line x1="218" y1="240" x2="1135" y2="240" stroke="var(--ink)" stroke-width="5"/><text x="12" y="245" font-family="var(--font-mono)" font-size="16" font-weight="600" fill="var(--ink)" stroke="none">develop</text><line x1="218" y1="315" x2="1090" y2="315" stroke="var(--p-b)" stroke-width="2"/><text x="12" y="320" font-family="var(--font-mono)" font-size="16" font-weight="600" fill="var(--p-b)" stroke="none">member-b</text>
<line x1="212" y1="44" x2="212" y2="385" stroke="var(--mut)" stroke-width="1.6" stroke-dasharray="5 5"/><circle cx="212" cy="315" r="5.5" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
```

**Work pill.** A feature on a track: a pill in the person's color, on `--panel`, with its name above it. When a merge decides, the same spot gets a new shape on that step. A chosen pill has a tint and a thick stroke. A dropped pill has a dashed muted outline and a white wash, with one line through the pill and one through its name. A side branch that never merged is a curve off the track to a dashed white pill, with a label that tells where it stopped.
```html
<rect x="330" y="303" width="84" height="24" rx="12" fill="var(--panel)" stroke="var(--p-b)" stroke-width="2"/><text x="372" y="295" font-size="15" text-anchor="middle" fill="var(--ink)" stroke="none">write</text><rect data-step="2" x="330" y="303" width="84" height="24" rx="12" fill="color-mix(in srgb, var(--p-b) 12%, var(--paper))" stroke="var(--p-b)" stroke-width="3.5"/>
<g data-step="2"><rect x="340" y="158" width="74" height="24" rx="12" fill="var(--paper)" fill-opacity=".75" stroke="var(--mut)" stroke-width="2" stroke-dasharray="4 4"/><line x1="348" y1="170" x2="406" y2="170" stroke="var(--mut)" stroke-width="2"/><line x1="350" y1="145" x2="404" y2="145" stroke="var(--ink)" stroke-width="2"/></g>
```

**Merge marks.** The mark says how the code arrived. A square is a merge from an integration branch. A filled circle is a merge from a person's PR. An open circle is a direct commit. A solid curve merges in. A dashed muted curve pulls the shared branch back to a person. A chosen person's curve is in that person's color at 2.8. Draw these kinds once in a key on the bottom line. Each marker color has its own id. Copy the marker from Whiteboard map.
```html
<path d="M414 315 C414 288 450 288 450 254" stroke="var(--p-b)" stroke-width="2.8" fill="none" marker-end="url(#SLOT-gg-b)"/><rect x="442" y="232" width="16" height="16" fill="var(--ink)"/><text x="436" y="228" font-family="var(--font-mono)" font-size="15" font-weight="600" text-anchor="end" fill="var(--ink)" stroke="none">PR 105</text><path d="M458 240 C458 268 505 268 505 300" stroke="var(--mut)" stroke-width="1.6" stroke-dasharray="5 5" fill="none" marker-end="url(#SLOT-gg-mut)"/>
<circle cx="920" cy="240" r="7" fill="var(--ink)"/><circle cx="1000" cy="240" r="5.5" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/>
```

**Decision card.** A white card above the graph at the merge that it explains. It has a bold title with the PR number, the criteria with accent circled numbers, and one mono result line. A thin dotted line drops from the card to the merge mark. The card comes with the merge, on one step.
```html
<g data-step="2"><rect x="290" y="56" width="300" height="92" rx="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="2"/><line x1="450" y1="148" x2="450" y2="228" stroke="var(--mut)" stroke-width="1.5" stroke-dasharray="3 4"/><text x="302" y="78" font-size="15" font-weight="700" fill="var(--ink)" stroke="none">PR 105 선택 기준</text>
  <text x="302" y="102" font-size="15" fill="var(--ink)" stroke="none"><tspan fill="var(--acc)" font-weight="700" font-size="19">①</tspan> 안정성  <tspan fill="var(--acc)" font-weight="700" font-size="19">②</tspan> 가독성</text><text x="302" y="130" font-family="var(--font-mono)" font-size="14" font-weight="600" fill="var(--ink)" stroke="none">→ args ← 멤버 C</text></g>
```

**Score strip.** One thick pale rounded line under the graph, with the pass counts on it in mono, each at the x of its merge. Each count shares a step with its merge. Only the last count is accent.
```html
<line x1="116" y1="415" x2="1150" y2="415" stroke="var(--grid)" stroke-width="22" stroke-linecap="round"/><text x="196" y="420" font-family="var(--font-mono)" font-size="14" font-weight="600" text-anchor="middle" fill="var(--ink)" stroke="none">18/95</text><g data-step="4"><text x="1120" y="422" font-family="var(--font-mono)" font-size="19" font-weight="700" text-anchor="middle" fill="var(--acc)" stroke="none">96/96</text></g>
```

**Zone cards.** Three equal cards, one per step, for a scale from left to right. Each has an accent disc with a white letter, a bold name, a muted line for the owner of the zone, and a thin rule. Rows have an accent mono id and a short line. The first cards are on `--panel`. The last card is on `--paper`, because no tool covers that zone. The disc letter is white on accent at size 26 or more.
```html
<g data-step="1"><rect x="20" y="24" width="360" height="300" rx="4" fill="var(--panel)" stroke="var(--ink)" stroke-width="2.5"/><circle cx="58" cy="66" r="22" fill="var(--acc)" stroke="none"/><text x="58" y="76" font-size="28" font-weight="700" text-anchor="middle" fill="var(--paper)" stroke="none">A</text><text x="92" y="64" font-size="26" font-weight="700" fill="var(--ink)" stroke="none">모양</text><text x="92" y="88" font-size="14" fill="var(--mut)" stroke="none">formatter · 저장하면 고쳐짐</text>
  <line x1="40" y1="104" x2="360" y2="104" stroke="var(--grid)" stroke-width="2"/><text x="40" y="136" font-family="var(--font-mono)" font-size="19" font-weight="700" fill="var(--acc)" stroke="none">A1</text><text x="84" y="136" font-size="17" font-weight="500" fill="var(--ink)" stroke="none">들여쓰기는 스페이스 4칸</text></g>
```

**Scope bracket.** Under the cards, an open bracket spans the zones that one command covers, with the command in bold mono below it. A wider bracket goes on a lower row. The bracket shares a step with the rightmost card that it covers.
```html
<g data-step="2"><path d="M30 384 L30 398 L750 398 L750 384" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="390" y="426" font-family="var(--font-mono)" font-size="19" font-weight="700" text-anchor="middle" fill="var(--ink)" stroke="none">make lint  (A + B 검사)</text></g>
```

**Editor squiggle.** Show a tool's complaint as the editor shows it: a zigzag polyline under the code in `--warn`, then the message beside it. Then give a pair of lines: a muted `✗` line with a strike, and a `✓` line in ink. `--warn` is 2.3:1, so use it only for the zigzag. Write the message in ink.
```html
<text x="420" y="210" font-family="var(--font-mono)" font-size="17" fill="var(--ink)" stroke="none">int FdCount;</text><polyline points="460 218 466 221 472 218 478 221 484 218 490 221 496 218 502 221 508 218 514 221 520 218 526 221" fill="none" stroke="var(--warn)" stroke-width="2"/><text x="548" y="210" font-size="15" font-weight="600" fill="var(--ink)" stroke="none">⚠ lower_case</text>
<text x="420" y="250" font-family="var(--font-mono)" font-size="17" font-weight="600" fill="var(--ink)" stroke="none">✓ int fd_count;</text>
```

## Do not

- Do not move a shape between map stops, and do not edit one stop by hand.
- Do not repeat the map without a lit region, and do not spend more than a few seconds on a stop.
- Do not redraw a screenshot when the real one fits. A rebuilt board comes after the real page.
- Do not put marks over an image with SVG or CSS. Mark the file, and only when the speaker talks through the marks.
- Do not add a hue for anything other than a person. Do not give one person two colors.
- Do not write a hex value in the deck, other than the person tokens and `--warn` in `:root`.
- Do not fit a figure by shrinking text. Split the slide (`reference/build.md`, density limits).
