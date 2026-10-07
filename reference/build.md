---
scope: The build phase (SPEC D9, D10, D17): style source, stage template, filling slides from BRIEF.md, viewport check
authority: SPEC.md D9, D10, D17. tests/test_build_revise_reference.py checks the rules here
status: draft 2026-10-07
---

# Build phase

The `build` phase writes the first draft of the deck (SPEC D9).
It starts when `BRIEF.md` has `phase: build`.
It ends when the deck renders and the student confirms the first draft.

Read these first:

1. `BRIEF.md` of the deck. The `Grill` section is your content. Do not ask again about a filled slot.
2. `jungle-deck.local.md` (keys: `reference/local-template.md`). You need `design_md`, `accent`, and `display_name`.
3. `reference/context.md`. It holds the room, the audience, and the language.

## Style source

Use the first source in this list that applies (D17). Do not mix sources.

1. **`design_md` is set.** Read that DESIGN.md. Put its color, font, and spacing tokens on `:root` in the deck. Follow its Do's and Don'ts. Do not run style discovery.
2. **`design_md` is empty, and the frontend-slides skill is installed.** Run its Phase 2 style discovery (mood, three previews, the student picks). Use this only when the skill is installed.
3. **`design_md` is empty, and frontend-slides is not installed.** Read `vendor/frontend-slides/STYLE_PRESETS.md`. Propose two or three presets that fit a bright lecture room and code on screen. Give one recommendation. The student picks.

For every source:

- The accent is the one in the `Accent and style` slot of `BRIEF.md`. It wins over the accent of the style source.
- Change only the token values on `:root` in the template. Do not add a second color set elsewhere in the CSS.
- Write the source you used in the `Build` section of `BRIEF.md`, on the `Template version` line. Example: "stage.html; style: DESIGN.md".

## Start from the stage template

1. Copy `templates/stage.html` to `<week repo>/study/<slug>/<slug>.html`. The slug is the `slug` in the `BRIEF.md` front matter.
2. Open the week repo's `.gitignore` (create it if it is missing). Add each of these lines that is not there yet (D13):

   ```
   _backup/
   previews/
   .impeccable/
   ```

   Do this now, before revise. In revise, `scripts/pull_edits.py` writes backups into `_backup/` next to the deck. Commit this `.gitignore` change together with the deck in publish.
3. Do not write a deck from zero. The template holds the stage runtime: one fixed slide at a time, the `#N` hash, `data-step` reveals, speaker notes on `N`, edit mode on `E`, and `Ctrl+S` export.
4. Keep the runtime script and the edit-mode CSS as they are.
5. Keep one `<section class="slide" id="sN">` per slide. Keep each section id stable after the first draft. `scripts/pull_edits.py` merges the student's edits by section id. A changed id loses those edits.
6. Write the section ids into the `Slide theses` table of `BRIEF.md` (column `Section id`).

The template has four example slides: title, code panels, takeaway, closing. Copy the slide shape you need, one section per row of the `Slide theses` table. Delete the example slides you do not use.

## Fill the slides

Fill each slide from its row in `BRIEF.md`.

- **Theses.** Put each thesis on its slide verbatim, as the student wrote it in `Slide theses`. Do not rephrase, shorten, or fix it. If a thesis does not fit the slide, change the layout or the font size, or ask the student. Do not change the words.
- **Conclusion and closing line.** Put them on the slides that `BRIEF.md` names, verbatim.
- **Evidence.** Fill evidence panels only from real runs saved in `evidence/`. Use the file that the `Evidence list` names for that slide. If the log is missing, re-run the command from the `How it was made` column. Save the output to `evidence/` first, then paste from that file. Never invent output, and never type output from memory. You may cut lines from a log; mark each cut with the template's `c-dim` elided line (`⋮ 생략`).
- **Terms.** Give each term in `Terms to define on screen` its on-screen definition on the slide that the table names. Do not leave a definition only in the speaker notes.
- **Speaker notes.** Write each `<aside class="notes">` as a light suggested script: one or two short lines per step, in the student's language. The student speaks in their own words. The notes are a prompt, not a text to read aloud. Tie a line to a step with `<span class="st">▸N</span>`.
- **Speaker name.** Use `display_name` from `jungle-deck.local.md`.

## Time is background

The 2-minute talk is background, not a gate (D10).

- No timer check. Do not count words, time the notes, or block the draft on a time estimate.
- Do not cut content only to fit a timer. Cut a slide only when the story or the density limits below need it.
- The `data-sec` value on a notes block is a pace hint in the notes panel. It is not a limit. Do not check the deck against it.

## Viewport and density

The deck shows on a large monitor in a bright room. Every slide must fit the screen with no scroll.

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

- If a slide goes over a limit, split it into two slides, or cut log lines. Never scroll, and never shrink text below the template's tokens. A split adds a row to `Slide theses`; ask the student to write that thesis.

## Check the render

Open the deck in a browser and check every slide, every step, at two sizes:

1. 1280×720
2. 1920×1080

At each size, look for these faults: text cut off at an edge, a panel taller than the slide, overlapping elements, a step that never shows. Also open the notes with `N` and check that each slide has notes.

Fix each fault in the source deck, then check again. Write any fault you cannot fix into `Open issues for revise` in the `Build` section of `BRIEF.md`.

## Finish

1. Fill the `Build` section of `BRIEF.md`: the deck file, the template version and style source, the open issues.
2. Tell the student the deck path. Tell them how to open it and that `E` starts edit mode.
3. Ask the student to confirm the first draft. Wait for the answer.
4. Move `phase` to `revise` only when the student confirms the draft. A rendered deck is not enough. In the same edit, set `updated` and rewrite `Next action`. Example: "Student edits in the browser and exports with Ctrl+S; then run pull_edits.py dry-run."
5. Then read `reference/revise.md`.
