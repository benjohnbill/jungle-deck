# BRIEF.md template and phase contract

Each deck has one `BRIEF.md` in `<week repo>/study/<deck-slug>/` (D5).
BRIEF.md holds the whole state of the deck (D4). The conversation does not.
A fresh session must find its next action in BRIEF.md alone.

## Phases

The phase order is `grill → build → revise → publish → done` (D3).

| `phase` | Work in this phase | The phase is done when |
|---|---|---|
| `grill` | Collect context (D8). Settle the six D7 decisions. | All six D7 slots are filled and the student confirms them. |
| `build` | Write `<deck-slug>.html` from the stage template and the Grill section. | The deck renders and the student confirms the first draft. |
| `revise` | Merge the student's browser edits. Fix layout and evidence. Repeat. | The student says to publish. |
| `publish` | Commit, copy, push, and verify the live deck (D12–D14). | The live deck matches the source and the index card is live. |
| `done` | Nothing. | — |

## How to resume

1. Read `BRIEF.md`. If it does not exist, copy the skeleton below and start at `grill` (D6).
2. Read `phase` in the front matter. Go to that phase. Skip every earlier phase (D4, D6).
3. Read the `Next action` section. Do that action first.
4. Do not ask the student again about a filled slot. A filled slot is settled.

## Who changes `phase`

- The agent writes the new `phase` value. The student does not need to edit the file.
- The agent moves `phase` forward only when the student confirms the phase is done. A finished task list is not enough.
- The agent moves `phase` one step at a time, in the order above.
- The agent never moves `phase` backward on its own. Only the student can send the deck back to an earlier phase. Example: "구성부터 다시 하자" sends it back to `grill`.
- When the agent changes `phase`, it also sets `updated` and rewrites `Next action` in the same edit.

## Rules for every edit

- Set `updated` to today's date (`YYYY-MM-DD`) on every edit.
- Keep `Next action` to one or two concrete steps. Write it before the session ends.
- Write a slot as `TBD` until it is settled. Replace `TBD` only with a value the student chose.
- The student writes the slide theses in D7 item 3. The agent copies them as written and does not rephrase them.
- For D7 items 1, 2, 4, 5, and 6, the agent proposes candidates and the student chooses. Record only the choice. Do not record the rejected candidates.
- Record a path relative to the deck folder, for example `evidence/gdb-run.txt`.

## Skeleton

Copy this block to `<week repo>/study/<deck-slug>/BRIEF.md`. Replace the example values.

```markdown
---
phase: grill
slug: bsize-cast
week: 6
deck: study/bsize-cast/bsize-cast.html   # relative to the week repo root
updated: 2026-10-07
---

# BRIEF — bsize-cast

## Next action

Collect context (D8). Then propose candidates for the conclusion.

## Grill

### Context notes

What context collection found: week repo commits, README and notes, the progress memo. Keep it short.

TBD

### Conclusion and closing line

D7 (1). One sentence, lead-first. It goes on an early slide. Then the line that closes the talk.

- Conclusion: TBD   (example: "size_t를 int로 캐스팅한 한 줄이 힙 전체를 깨뜨렸다")
- Closing line: TBD

### Story frame

D7 (2). Pick one.

- [ ] 起承轉結, 7 slides: title, hook, 起, 承, 轉, 結, takeaway
- [ ] symptom → evidence → cause, 6 slides

### Slide theses

D7 (3). One sentence per slide. The student writes each sentence. The agent does not edit them.

| # | Section id | Role | Thesis (student's words) |
|---|---|---|---|
| 00 | s00 | Title | TBD |
| 01 | s01 | TBD | TBD |

### Evidence list

D7 (4). Real output only. Each item names its source run and its slide.

| Slide | Evidence | File in `evidence/` | How it was made |
|---|---|---|---|
| TBD | TBD (example: gdb backtrace at the crash) | TBD (example: evidence/gdb-bt.txt) | TBD (example: `gdb -batch -ex run -ex bt ./mdriver`) |

### Accent and style

D7 (5). The accent color and any style variation for this deck.

- Accent: TBD   (example: `#ff3300`, or the preferred accent from local.md)
- Variation: TBD   (example: "none" or "cobalt variant")

### Terms to define on screen

D7 (6). Terms the audience may not know. Each gets a short on-screen definition.

| Term | On-screen definition | Slide |
|---|---|---|
| TBD (example: `GET_SIZE`) | TBD | TBD |

## Build

What `build` produced. Filled by the agent.

- Deck file: TBD
- Template version: TBD
- Open issues for `revise`: TBD

## Revise

One line per round. The student edits in the browser and exports. The merge script merges the export. The agent then adjusts layout and evidence.

| Round | Date | Export merged | What changed |
|---|---|---|---|
| 1 | TBD | TBD | TBD |

## Publish

What `publish` did. The student approves the push once.

- Week repo commit: TBD
- Pages copy path: TBD
- Pages repo commit: TBD
- Push approved by student: TBD
- Live URL (HTTP 200, `cmp` match): TBD
- Index card found: TBD
- DESIGN.md items applied: TBD
```
