---
scope: The build phase (SPEC D9, D10, D13): stage template, style from the Design section, images, filling slides and notes from BRIEF.md, viewport check, usage guidance
authority: SPEC.md D7, D9, D10, D13. tests/test_build_revise_reference.py checks the rules here
status: revised 2026-10-29 (figures); unverified draft (D19)
---

# Build phase

The `build` phase writes the first draft of the presentation (SPEC D9).
It starts when `BRIEF.md` has `phase: build`.
It ends when the page renders and the student confirms the first draft.

Read these first:

1. `BRIEF.md`. The `Grill` section is your content, and the `Design` section is your style. Do not ask again about a filled slot.
2. `jungle-deck.local.md` (keys: `reference/local-template.md`). You need `display_name` and `python_cmd`.
3. `reference/context.md`. It holds the room, the audience, and the language.

## Start from the stage template

1. Copy `templates/stage.html` to `<save folder>/<slug>.html`. The slug is the `slug` in the `BRIEF.md` front matter.
2. Check `<save folder>/.gitignore`. Add each of these lines that is missing: `_backup/`, `previews/`, `.impeccable/`, `.serve.json`, `.serve.log` (D13). Never edit the `.gitignore` at the repo root.
3. Do not write a page from zero. The template holds the stage runtime: one fixed slide at a time, the `#N` hash, `data-step` reveals, speaker notes on `N`, edit mode on `E`, save on `Ctrl+S`, the `?` shortcut overlay, and the first-open hint.
4. Keep the runtime script and the edit-mode CSS as they are.
5. Keep one `<section class="slide" id="sN">` per slide. Keep each section id stable after the first draft. Every save in revise matches sections by id. A changed id loses the student's edits.
6. Write the section ids into the `Slide theses` table of `BRIEF.md` (column `Section id`).

The template has four example slides: title, code panels, takeaway, closing. Copy the slide shape you need, one section per row of the `Slide theses` table. Delete the example slides you do not use.

## Style

Read the style only from the `Design` section of `BRIEF.md` (D9). The design phase settled it (`reference/design.md`).

- Write the `Tokens` values to `:root` in the page: the six color tokens and the two font stacks. Keep each fallback as `Tokens` marks it.
- Set `--acc` to the `Accent` value.
- Change only the token values on `:root`. Do not add a second color set elsewhere in the CSS.

If the `Design` section has a `TBD`, the design phase is not done. Tell the student, and propose to set `phase` back to `design`. Build nothing until the student answers.

## Images

An image on a slide comes from `evidence/`, like any other evidence.

- Copy the file from `evidence/` into `<save folder>/<slug>.assets/`. The original stays in `evidence/`.
- Reference it as `<slug>.assets/<file>`, a path relative to the page. Never embed an image as a `data:` URI.
- Use `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, or `.avif`. The revise server does not serve `.svg`: convert an SVG to PNG first.

## Fill the slides

Fill each slide from its row in `BRIEF.md`.

- **Theses.** Put each thesis on its slide verbatim, as `Slide theses` records it. Do not rephrase, shorten, or fix it. If a thesis does not fit the slide, change the layout or the font size, or ask the student. Do not change the words.
- **Title slide and closing line.** Put them on the first and the last slide, verbatim.
- **Evidence.** Fill evidence panels only from real runs saved in `evidence/`. Use the file that the `Evidence list` names for that slide. If the log is missing, re-run the command from the `How it was made` column in `source_repo`. Save the output to `evidence/` first, then paste from that file. Never invent output, and never type output from memory. You may cut lines from a log; mark each cut with the template's `c-dim` elided line (`⋮ 생략`).
- **Lock the evidence.** In edit mode the student can change every element that holds text of its own. Put `data-evidence` on each element that holds real run output: the `<pre>` of a log, a figure with a screenshot. The page locks it and everything inside it. Explanatory code and diagram boxes that you write stay editable. Give a diagram box the class `box` (or the attribute `data-box`), so the student can change its width. Do not set the size classes `jd-t-*` and `jd-w-*`: they are the student's size steps.
- **Terms.** Give each term in `Terms to define on screen` its on-screen definition on the slide that the table names. Do not leave a definition only in the speaker notes.
- **Speaker notes.** Read the `Script` slot.
  - It holds a script: put each slide's part into that slide's `<aside class="notes">`, as the student confirmed it. Then replace the slot text with `build에서 노트로 옮김 — 이후 수정은 페이지에서`. From now on the page notes are the script; the student edits them on the page.
  - It says `없음 — build가 가벼운 노트를 씀`: write each notes block as a light suggested script: one or two short lines per step, in the student's language. The student speaks in their own words.
  - Tie a line to a step with `<span class="st">▸N</span>`.
- **Speaker name.** Use `display_name`. When it is `""`, leave the name off the title slide.

## Figures

The presentation is visual first. A slide whose `Show` line names an order, a branch, a path, a layout, or a quantity gets a figure under its thesis, with `data-step` reveals. Use bullets only for a list with no shape.

- Read `vendor/diagram-design/SKILL.md` before the first figure, and follow its slide-scale overrides.
- Draw only what the `Show` line names (D10: selecting by the thesis is not cutting for time).
- A few labeled boxes that the student may retype: HTML boxes with the class `box`. Arrows, a sequence, a flowchart, a memory layout, or a chart: one inline `<svg>`. Edit mode cannot change SVG text, so the student asks for a figure change in revise.
- Never link an `.svg` file. The revise server does not serve it.

## Time is background

The 2-minute talk is background, not a gate (D10).

- No timer check. Do not count words, time the notes, or block the draft on a time estimate.
- Do not cut content only to fit a timer. Cut a slide only when the story or the density limits below need it.
- The `data-sec` value on a notes block shows as "참고 시간" in the notes panel. It is a pace hint, not a limit. Do not check the page against it.

## Viewport and density

The page shows on a large monitor in a bright room. Every slide must fit the screen with no scroll.

- The template already holds the viewport contract from `vendor/frontend-slides/viewport-base.css`. Keep it. Every slide is one viewport high, with `overflow: hidden`.
- Use the template's `clamp()` size tokens for new text. Do not set a fixed `px` font size.
- Keep each slide within the frontend-slides density limits:

| Slide type | Maximum content |
|---|---|
| Title | 1 heading, 1 subtitle, 1 optional tagline |
| Content | 1 heading and 4–6 bullets, or 1 heading and 2 paragraphs |
| Code or log | 1 heading and 8–10 lines per panel |
| Grid | 1 heading and 6 cards |
| Image | 1 heading and 1 image, height at most 60vh |
| Figure | 1 heading and 1 figure: 6 or fewer nodes, rows, or bars, and 4 or fewer steps |

- If a slide goes over a limit, split it into two slides, or cut log lines. Never scroll, and never shrink text below the template's tokens. A split adds a row to `Slide theses`. Its thesis follows the proposal rule (`reference/grill.md`).

## Check the render

Run the layout check once, from the skill directory:

```
<python_cmd> scripts/check_layout.py <save folder>/<slug>.html
```

It renders every slide with every step shown, at 1280×720 and 1920×1080, and prints one line per section: `ok`, or the overflow and overlap it found. Exit 0: every section fits. Exit 1: fix each listed section (split it, or cut log lines, as in "Viewport and density"), then run it once more. `small text` names figure text under 12 px: make the viewBox no larger than the slot, or split the figure. Do not lower the font size. Exit 2: read the error line. Exit code 3 means no headless browser (Chrome, Chromium, or Edge) was found: skip the check (D15).

Do not write a screenshot tool of your own, and do not run a screenshot-and-fix loop. The script cannot judge looks, a step that never shows, or an image that does not load: the student opens the page and gives that feedback (Finish, step 4).

Write any fault you cannot fix into `Open issues for revise` in the `Build` section of `BRIEF.md`.

## Finish

1. Fill the `Build` section of `BRIEF.md`: the page file and the open issues.
2. Start the revise server now, as in "Start the server" of `reference/revise.md`, so the student sees the draft at the address that saves.
3. Give the student three lines in the terminal, in Korean:
   1. How to open: the server address `http://127.0.0.1:<port>/<slug>.html`.
   2. The keys: `→` next, `N` notes, `E` edit, `Ctrl+S` save, `?` all shortcuts.
   3. After an edit: "고친 뒤 저장하고 에이전트에게 말해 주세요".
4. Ask the student to look through the first draft in the browser and say what to change, or confirm it. Wait for the answer.
5. Move `phase` to `revise` only when the student confirms the draft. A rendered page is not enough. In the same edit, set `updated` and rewrite `Next action`. Example: "Student edits and saves in the browser, then says 저장했어; read the last line of .serve.log."
6. Then read `reference/revise.md`.
