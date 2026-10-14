---
scope: The revise phase (SPEC D11, D15): revise server, save in the page, read the change, adjust, conflicts, and the file-export fallback with pull_edits.py
authority: SPEC.md D11, D15, "Revise server". CLI lines here must match `scripts/serve.py --help` and `scripts/pull_edits.py --help`; page behaviour must match templates/stage.html. tests/test_build_revise_reference.py checks them
status: revised 2026-10-15 (#21, #28); unverified draft (D19). Not verified yet: whether a `run_in_background` server outlives the Claude Code session (SPEC "Verification plan"); record the result here
---

# Revise phase

The `revise` phase is the main loop of the skill (SPEC D11).
It starts when `BRIEF.md` has `phase: revise`.
It ends only when the student says to publish.

The student owns the words. The student edits them in the browser and saves.
The agent owns the layout and the evidence.

## Rules

- Do not overwrite the student's wording. After a save, the student's text is the source of truth. Change layout, size, steps, and evidence around it. If a layout fix needs other words, propose them under the proposal rule (`reference/grill.md`) and use the student's pick.
- Keep every `<section id>` stable. Every save matches sections by id.
- **Edit rule.** Change `<slug>.html` only with targeted edits on a fresh read. A student save can land between your read and your write. A write from an older read deletes that save. Use an edit that fails when the file changed since you read it. In Claude Code, that is the Edit tool. Never rewrite the whole file from an older read: no whole-file Write, and no script of your own that reads the page, changes it, and writes it back. `pull_edits.py --write` is the exception: it reads the page and writes it in one short call, and you guard it as in its fallback step. When an edit fails, re-read the page. Then read every line of `.serve.log` that is newer than your last read, not only the last line: a later `save (no change)` can hide an earlier save. Handle each save as in loop steps 4 and 5 first. Then redo the edit on the new text.
- Every write to the page, by the server or by `pull_edits.py`, first copies the page to `_backup/<slug>.<YYYYmmdd-HHMMSS>.html`. `_backup/` is in the save folder's `.gitignore` (D13).

## Start the server

Do this at revise entry, and at the end of build.

1. Read `<save folder>/.serve.json` (`{port, pid}`). If it exists, request `http://127.0.0.1:<port>/version`. Reuse that server only when it answers and its `source` is the resolved absolute path of `<save folder>/<slug>.html` (symlinks resolved, as `realpath` prints it).
2. Else start a new server with the Bash tool and `run_in_background`, from the skill directory:

   ```
   <python_cmd> scripts/serve.py --deck <save folder>/<slug>.html
   ```

   It prints `serving http://127.0.0.1:<port>/<slug>.html` and rewrites `.serve.json`. It exits non-zero when the page is missing or no port is free.
3. Give the student the address `http://127.0.0.1:<port>/<slug>.html`. This is the one address that saves. The page opened as a file does not save to the source; see "Fallback: no server".

## The loop

One pass is one round.

1. **Student edits.** On the server address, the student presses `E` for edit mode and changes slide text or notes.
2. **Student saves.** The student presses Ctrl+S. The page sends only the sections the student changed. The server writes each one only when its source section still holds what the page loaded (a three-way merge per section). The page shows "저장했어요 (<ids>)".
3. **Student tells you.** The default: the student says "저장했어, 봐줘" or similar.
   Where the Claude Code `Monitor` tool works, you may also run `tail -n0 -F <save folder>/.serve.log` under it and start step 4 on each new line by yourself. Without `Monitor`, wait for the student (D15).
4. **Read the log.** Read the last line of `.serve.log`. Check that its time is newer than the line of the last round: a save with no change in the page sends nothing and writes no line. An old line: ask the student whether the page said "바뀐 곳이 없어요". Its forms:
   - `<time> save <ids> backup=<path>`: the server wrote those sections. Go to step 5.
   - `<time> save (no change)`: nothing changed. Ask the student whether they saved after the edit.
   - `<time> 409 <ids> payload=<path>`: nothing was written. Go to "When the save is refused".
5. **Read the diff.** Run `diff -u <backup> <save folder>/<slug>.html` with the backup path from the log line. Tell the student about any change that looks accidental (for example, a deleted panel or a stray character). Undo it only when the student says so, under the edit rule.
6. **Adjust.** Fix the layout and the evidence to match the student's edits, without changing their words. Every change follows the edit rule (Rules):
   - A longer thesis or note: change the layout or the size token, not the text.
   - A slide that now goes over the density limits in `reference/build.md`: split it, or cut log lines. The thesis of a new slide follows the proposal rule (`reference/grill.md`).
   - New evidence that the student asks for: take it only from real runs saved in `evidence/`. Re-run the command in `source_repo` if the log is missing. Never invent output.
   - Check the render again at 1280×720 and 1920×1080, as in `reference/build.md`.
7. **Record.** Add one row to the `Revise` table of `BRIEF.md`: the round, the date, and what changed. Write the notable changes only: a new or split slide, a changed thesis, new evidence, a layout fix. Set `updated` and rewrite `Next action`.
8. **Hand back.** Tell the student the page is ready. When you changed the page, it shows "에이전트가 수정했어요 — R로 새로고침" within a few seconds. `R` reloads and keeps the slide number.

Then repeat from step 1.

## What the student sees

While served, the page checks the source every 3 s. After two failed checks it checks every 30 s and shows the server-off notice.

| Notice in the page | Meaning | What you do |
|---|---|---|
| "에이전트가 수정했어요 — R로 새로고침" | You changed the source; the page has no unsaved edits. | Tell the student to press `R`. |
| "에이전트가 수정했어요 — 먼저 저장(Ctrl+S)하세요" | You changed the source while the student had unsaved edits. | Tell the student to save first. A section that you both changed gets a 409. |
| "저장 안 된 편집이 있어요 (<ids>) — 그 뒤에 파일이 바뀌었어요", with "복원", "파일로 내보내기", "닫기" | The page kept edits that were never saved, and the file changed after them. | Tell the student to press "복원". On the server it is a normal save of those sections: read the log as in step 4. |
| "자동 저장이 안 돼요 — 지금 Ctrl+S로 저장하세요" | The browser refused local storage. | Tell the student to save now. |

## When the save is refused

**409: the edit overlaps yours.** The page turns edit mode off and shows "에이전트 수정과 겹쳐요 (<ids>). 에이전트에게 '겹친 거 합쳐줘'라고 말해 주세요". The log line names the payload file `_backup/rejected-<stamp>.json`: `{"base_hash", "sections": {id: html}}`. The server wrote nothing.

1. Read the payload. Apply every section in it to the current page, not only the ids in the log line. The other sections were refused with them. Apply them under the edit rule (Rules).
2. For an id in the log line, the student's text wins: put their words into the current section, and keep your layout change where it does not touch the words.
3. Read the diff, then go on from loop step 6.
4. Ask the student to press `R`. After a 409 the page offers `R`, and the payload file holds the student's edits, so the reload loses nothing.

**The server is off.** The page shows "서버가 꺼져 있어요. 에이전트에게 '서버 다시 켜줘'라고 말해 주세요". A save that failed this way also exported the page to the downloads folder.

1. Start the server again, as in "Start the server". It takes the same port when that port is free.
2. Same address: tell the student to press Ctrl+S again. The page still holds the edits.
3. A new address: the browser keeps unsaved edits per address, so they are not on the new one. Merge the exported file with "Fallback: no server" from its dry-run, then give the student the new address.

**Another HTTP error.** The page shows "저장이 안 됐어요 (HTTP <n>) — 대신 파일로 내보냈어요". The server writes nothing and logs nothing for it; the status code is the only clue (403: the page was not opened at `127.0.0.1:<port>` or `localhost:<port>`; 413: the save is over 5 MB). Merge the exported file with "Fallback: no server".

## Fallback: no server

Use this path when the server cannot run or the browser cannot reach it (for example, WSL with `localhostForwarding=false`), or when the student opened the page as a file. Here Ctrl+S exports a copy of the page to the downloads folder, and `scripts/pull_edits.py` merges it back two-way, by section id.

Two-way means the export replaces each changed section whole. So do not edit the page while the student has edits in the browser that they did not export. Ask the student to export first.

1. **Student exports.** The student presses Ctrl+S. The browser saves a copy into the downloads folder. The copy does not replace the source.
2. **Dry-run.** Run `pull_edits.py` as a dry-run first, from the skill directory:

   ```
   <python_cmd> scripts/pull_edits.py --deck <save folder>/<slug>.html
   ```

   The script finds the newest export of the page in the downloads folder (`downloads_dir` in local.md; the first time, set it as `reference/local-template.md` says). If the export is in another place, give it with `--export <file>`, or give the folder with `--downloads <dir>`. The script prints a diff for each changed section, one summary line, and the exact `--write` command with the `--export` path of the file it read. It writes nothing.

   Show the student the summary line and the changed section ids. Read the diff yourself. Tell the student about any change that looks accidental. Ask the student to agree to the merge. Wait for the answer.

3. **Commit the page.** When the save folder is in a git repo, commit the page before the write. Stage only the page file. Example: `git -C <save folder> add <slug>.html`, then `git -C <save folder> commit -m "Page before revise round N"`. This commit is the second line of defence; the script backup is the first. When there is no repo, or the student does not want a commit now, tell the student that the script backup is the only copy.
4. **Write.** Run the `--write` command that the dry-run printed, only after the student agrees:

   ```
   <python_cmd> scripts/pull_edits.py --deck <save folder>/<slug>.html --export <export file from the dry-run> --write
   ```

   `--write` needs `--export`. Use the file that the dry-run read, so the export that the student reviewed is the export that is written.

   `--write` reads the page as it is at the write. The script copies the page to `_backup/` next to it, then replaces each changed section with the export's version. It does not change the head, the styles, or the scripts.

   When a server runs for this page, note the time when you run the dry-run; its output has no time. Before the write, read every line of `.serve.log` that is newer than the dry-run. If one of them is a save, run the dry-run again, and show the student the new diff before the write.

5. **Adjust and record** as in loop steps 6 and 7.
6. **Hand back.** Ask the student to reload the page before they edit again. An old tab would export its old sections over your changes.

In file mode, "복원" merges in the page. A slide that changed in the file too stays out, with "파일에서도 바뀐 슬라이드라 복원하지 못했어요 (<ids>). 파일로 내보내고 에이전트에게 말해 주세요". The student exports it; merge that file from step 2.

| Output | Meaning | Action |
|---|---|---|
| `--write needs --export FILE` | The write ran without the export path. | Run the `--write` command that the dry-run printed. |
| `downloads_dir is not set ...; using <dir> (detected)` | `downloads_dir` is not set in local.md. The script used the detected folder. | If the export is not there, ask the student for the downloads folder and write it to `downloads_dir`. |
| `downloads_dir is not set ... and no downloads folder was detected` | On WSL, the Windows profile was not found. | Ask the student for the downloads folder. Write it to `downloads_dir`, or pass it with `--downloads`. |
| `no <slug>*.html export in <dir>` | No export with the page's file name in that folder. | Ask the student where the browser saved the file. Pass it with `--export`. |
| `no matching sections` | The export is not this page, or the section ids changed. | Check the file name. Compare the section ids. Do not write. |
| `0 changed` | The export matches the source. | Nothing to merge. Ask the student whether they exported after the edit. |
| `missing in export` / `extra in export` | Section ids differ between the page and the export. | The script keeps missing sections and does not add extra ones. Tell the student which ids differ. |

## Leaving revise

- Move `phase` to `publish` only when the student says to publish. Examples: "게시하자", "발표 자료 게시", "publish". A clean round, a passing render check, or an empty `Open issues` list is not enough.
- Do not ask the student whether to publish after each round. Revise is open-ended. The student decides when the presentation is done.
- In the same edit, set `updated` and rewrite `Next action`. Example: "Ask whether to commit the presentation in this repo (D12)."
- Then read `reference/publish.md`.
