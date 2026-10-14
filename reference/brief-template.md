---
scope: The BRIEF.md file of one presentation: phases, save folder, resume, migration, skeleton
authority: SPEC.md D3-D7, D13, D17, D21, D23. Slot names here are a contract with the phase files and their tests; change them together
status: revised 2026-10-15; unverified draft (D19)
---

# BRIEF.md template and phase contract

Each presentation has one `BRIEF.md` in its save folder (D5).
BRIEF.md holds the whole state of the presentation (D4). The conversation
does not. A fresh session must find its next action in BRIEF.md alone.

## Phases

The phase order is `grill → design → build → revise → publish → done` (D3).

| `phase` | Work in this phase | The phase is done when |
|---|---|---|
| `grill` | Collect context (D8). Settle the content slots of the Grill section (D7). | Every Grill slot except `Script` is filled, and the student confirms "이 내용으로 디자인을 정할까요?". |
| `design` | Pick the style source, the previews, and the accent (D17). | The `Design` section is filled and the student confirms it. |
| `build` | Write `<slug>.html` from the stage template, the Grill section, and the `Design` section (D9). | The page renders and the student confirms the first draft. |
| `revise` | Merge the student's saves. Fix layout and evidence. Repeat (D11). | The student says to publish. |
| `publish` | Commit, copy, push, and verify the live page (D12–D14). | Every step that the student said yes to is verified. |
| `done` | Nothing. | — |

## Save folder

When a new presentation starts, ask "이번 주 발표 자료를 어디에 저장할까요?".
The default is `<current directory>/<slug>/`. The folder need not be in a
git repo. No `weekNN/` layout is assumed.

The save folder holds `BRIEF.md`, `<slug>.html`, `<slug>.assets/` (images),
`evidence/`, and its own `.gitignore`. Write that `.gitignore` when you create
the folder, with these lines: `_backup/`, `previews/`, `.impeccable/`,
`.serve.json`, `.serve.log` (D13). Edit no other `.gitignore`.

Then fill the front matter:

- `kind: jungle-deck` marks the file. A file without it is a BRIEF only in the old format (see "How to resume").
- `deck` is relative to the save folder: `<slug>.html`.
- `source_repo` is the git repo of the directory where the skill was called
  (`git rev-parse --show-toplevel`). It can differ from the save folder (D8).
- `week` is optional (D21). When a part of the save path matches `week\d+`,
  write its number. Else leave it empty. Never ask the student for it.
- `created` is today's date. Set it once; never change it.
- In `jungle-deck.local.md`, move the old `current_brief` value to
  `prev_brief`, then set `current_brief` to the new BRIEF.md path (D16).

## How to resume

1. Find BRIEF.md. Search in this order and stop at the first hit:
   `<cwd>/BRIEF.md`, then `<cwd>/*/BRIEF.md` (depth 1), then the path in
   `current_brief` of local.md. A file counts when its front matter has
   `kind: jungle-deck`, or has `phase:`, `slug:`, and `deck:` (the old
   format). If more than one file matches at one level, ask which one, as a
   numbered list.
2. If the file is in the old format, migrate it first (see "Migration from
   the old format").
3. If no file is found, start a new presentation: ask for the save folder,
   copy the skeleton below, and start at `grill` (D6).
4. Read `phase` in the front matter. Go to that phase. Skip every earlier
   phase (D4, D6).
5. Read the `Next action` section. Do that action first.
6. A filled slot is settled. Use it; do not ask about it again.

## Who changes `phase`

- The agent writes the new `phase` value. The student does not need to edit the file.
- The agent moves `phase` forward only when the student confirms the phase is done. A finished task list is not enough.
- The agent moves `phase` one step at a time, in the order above.
- The agent moves `phase` backward only when the student asks. Example: "구성부터 다시 하자" sends it back to `grill`.
- When the agent changes `phase`, it also sets `updated` and rewrites `Next action` in the same edit.

## Rules for every edit

- Set `updated` to today's date (`YYYY-MM-DD`) on every edit.
- Keep `Next action` to one or two concrete steps. Write it before the session ends.
- Write a slot as `TBD` until it is settled.
- Proposal rule (D7): for every slot, the agent proposes 1–3 candidates or a draft and recommends one. The recorded text is the student's pick or rewrite. Record only that text, not the other candidates.
- Record a path relative to the save folder, for example `evidence/gdb-run.txt`.

## Migration from the old format

An old BRIEF.md has `phase:`, `slug:`, and `deck:` in its front matter and no
`kind` line (D23). Migrate it once, in one edit:

1. Add `kind: jungle-deck`.
2. Add `created`: the date of the first commit that touched the BRIEF
   (in the save folder: `git log --follow --format=%as -- BRIEF.md | tail -n 1`),
   else the `updated` value.
3. At `phase: grill`: add each new slot as `TBD` — Metadata, Story frame
   (the two questions), Title slide, Script, and the Design section. Keep every
   filled slot. The old `Conclusion` slot maps to the title slide: copy its
   text into the Title slide slot.
4. At `build` or later: change nothing else. The phase already used the old
   slots.

An old `deck:` value can be relative to the git repo root, not to the save
folder. When `<save folder>/<deck>` does not exist, read the page at
`<repo root>/<deck>`. Do not rewrite the value.

## Skeleton

Copy this block to `<save folder>/BRIEF.md`. Replace each placeholder in angle brackets.

```markdown
---
kind: jungle-deck
phase: grill
slug: <slug>
week: <N, or empty>
deck: <slug>.html   # relative to the save folder
source_repo: <absolute path of the git repo where the skill was called>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# BRIEF — <slug>

## Next action

Collect context (D8). Then run the context check-in with the metadata round.

## Grill

### Context notes

What context collection found, and what it could not read. Keep it short.

TBD

### Metadata

D7 (2). Settled in the same round as the context check-in.

- What to present: TBD
- Why: TBD
- The one line the audience should take away: TBD   (it steers the grilling; it need not be on a slide)
- Slide count: TBD   (suggest 6 ± 2; a suggestion, not a rule)

### Story frame

D7 (3). Two questions. A frame fixes no slide count.

- Structure: TBD   (오프닝 → 도입 → 전개 → 전환 → 마무리, recommended; or 증상 → 증거 → 원인)
- Opening: TBD   (common ground, which may link to last week's topic; or a plain topic introduction with the student's motive)

### Title slide and closing line

D7 (4). The title slide states the point, lead-first. Then the line that closes the talk.

- Title slide: TBD
- Closing line: TBD

### Slide theses

D7 (5). One sentence per slide.

| # | Section id | Role | Thesis |
|---|---|---|---|
| 01 | s1 | Title | TBD |
| 02 | s2 | TBD | TBD |

### Evidence list

D7 (6). Real output only. Each item names its source run and its slide.

| Slide | Evidence | File in `evidence/` | How it was made |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

### Terms to define on screen

D7 (7). Terms the audience may not know. Each gets a short on-screen definition.

| Term | On-screen definition | Slide |
|---|---|---|
| TBD | TBD | TBD |

### Script

D7 (8), optional. Ask "발표 스크립트를 먼저 만들까요?". Yes: a full per-slide script here. No: write `없음 — build가 가벼운 노트를 씀`. After build, replace the script with `build에서 노트로 옮김 — 이후 수정은 페이지에서` (D9).

TBD

## Design

Filled in `design` (D17). `build` reads the style only from this section (D9).

- Source: TBD   (the student's DESIGN.md path, a reference URL or image, `getdesign.md/<brand>`, a frontend-slides discovery pick, or a vendored preset)
- Tokens: TBD   (`--paper`, `--ink`, `--acc`, `--mut`, `--panel`, `--grid`, and the fonts)
- Accent: TBD

## Build

What `build` produced. Filled by the agent.

- Page file: TBD
- Open issues for `revise`: TBD

## Revise

One line per round. The student saves in the browser; the agent reads the change and adjusts layout and evidence.

| Round | Date | What changed |
|---|---|---|
| 1 | TBD | TBD |

## Publish

What `publish` did (D12–D14).

- Commit in this repo (the commit, or "not a git repo"): TBD
- Separate deploy (student's answer): TBD
- Pages copy path: TBD
- Pages repo commit: TBD
- Push approved by student (one answer for commit and push, this pass): TBD
- Live URL (HTTP 200, `cmp` match): TBD
- Index card found: TBD
- DESIGN.md feedback: TBD
```
