---
scope: The revise phase (SPEC D11): browser edit, export, merge back with pull_edits.py, adjust, repeat
authority: SPEC.md D11. CLI lines here must match `scripts/pull_edits.py --help`; tests/test_build_revise_reference.py checks them
status: draft 2026-10-07
---

# Revise phase

The `revise` phase is the main loop of the skill (SPEC D11).
It starts when `BRIEF.md` has `phase: revise`.
It ends only when the student says to publish.

The student owns the words. The student edits them in the browser.
The agent owns the merge, the layout, and the evidence.

## Rules

- Do not overwrite the student's wording. After a merge, the student's text is the source of truth. Change layout, size, steps, and evidence around it. If a layout fix needs other words, ask the student.
- Do not edit the source deck while the student has edits in the browser that they did not export. The deck autosaves edits in the browser. When the source file changes, the deck moves that autosave aside and shows the file. Ask the student to export first.
- `scripts/pull_edits.py` has no backup of its own. Before every write, commit the deck or copy it (step 4 below).
- Keep every `<section id>` stable. The merge matches sections by id. A new section in the export is not added; a section missing from the export is kept as is.

## The loop

Run these steps in order. One pass is one round.

1. **Student edits.** The student opens the deck in a browser and presses `E` for edit mode. They click slide text or notes and change it.
2. **Student exports.** The student presses Ctrl+S. The browser saves a copy of the deck into the downloads folder. The copy does not replace the source.
3. **Dry-run.** Run `pull_edits.py` as a dry-run first, from the skill directory:

   ```
   python3 scripts/pull_edits.py --deck <week repo>/study/<slug>/<slug>.html
   ```

   The script finds the newest export of the deck in the downloads folder. If the export is in another place, give it with `--export <file>`, or give the folder with `--downloads <dir>`. The script prints a diff for each changed section and one summary line. It writes nothing.

   Show the student the summary line and the changed section ids. Read the diff yourself. Tell the student about any change that looks accidental (for example, a deleted panel or a stray character). Ask the student to agree to the merge. Wait for the answer.

4. **Back up the deck.** Before the write, commit the deck or copy the deck:
   - Commit: in the week repo, stage only the deck file and commit it. Example: `git -C <week repo> add study/<slug>/<slug>.html`, then `git -C <week repo> commit -m "Deck before revise round N"`.
   - Copy: `cp <deck> <week repo>/study/<slug>/_backup/<slug>-round-N.html`. `_backup/` is gitignored (D13).

   Do not go to step 5 without one of the two.

5. **Write.** Run the same command with `--write`, only after the student agrees:

   ```
   python3 scripts/pull_edits.py --deck <week repo>/study/<slug>/<slug>.html --write
   ```

   Give the same `--export` or `--downloads` value as in the dry-run. The script replaces only the changed sections. It does not change the head, the styles, or the scripts.

6. **Adjust.** Read the merged deck. Fix the layout and the evidence to match the student's edits, without changing their words:
   - A longer thesis or note: change the layout or the size token, not the text.
   - A slide that now goes over the density limits in `reference/build.md`: split it, or cut log lines. Ask the student for the thesis of a new slide.
   - New evidence that the student asks for: take it only from real runs saved in `evidence/`. Re-run the command if the log is missing. Never invent output.
   - Check the render again at 1280×720 and 1920×1080, as in `reference/build.md`.

7. **Record.** Add one row to the `Revise` table of `BRIEF.md`: the round, the date, the export file, and what changed. Write the notable changes only: a new or split slide, a changed thesis, new evidence, a layout fix. Set `updated` and rewrite `Next action`.
8. **Hand back.** Tell the student the deck is ready for the next round. Ask them to reload the page before they edit again.

Then repeat from step 1.

## When the script fails

| Output | Meaning | Action |
|---|---|---|
| `no <slug>*.html export in <dir>` | No export with the deck's file name in that folder. | Ask the student where the browser saved the file. Pass it with `--export`. |
| `no matching sections` | The export is not this deck, or the section ids changed. | Check the file name. Compare the section ids. Do not write. |
| `0 changed` | The export matches the source. | Nothing to merge. Ask the student whether they exported after the edit. |
| `missing in export` / `extra in export` | Section ids differ between the deck and the export. | The script keeps missing sections and does not add extra ones. Tell the student which ids differ. |

## Leaving revise

- Move `phase` to `publish` only when the student says to publish. Examples: "게시하자", "덱 게시", "publish". A clean round, a passing render check, or an empty `Open issues` list is not enough.
- Do not ask the student whether to publish after each round. Revise is open-ended. The student decides when the deck is done.
- In the same edit, set `updated` and rewrite `Next action`. Example: "Commit the deck, BRIEF.md, and evidence/ in the week repo."
- Then read `reference/publish.md`.
