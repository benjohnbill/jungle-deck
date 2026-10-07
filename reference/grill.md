# Grill phase

The `grill` phase settles the design of one deck (SPEC D7, D8).
It starts when `BRIEF.md` has `phase: grill`, or when no `BRIEF.md` exists (D6).
It ends when all six decisions are in `BRIEF.md` and the student confirms them.

Read `reference/context.md` first. It holds the setting that is the same for every Jungle talk.
Do not ask the student about a row in that file. Those rows are defaults, not questions.

## Context collection

Do this at the start of every `grill` phase, before the first question (D8).
Collect facts yourself. Do not ask the student for a fact you can find.
Read the sources in this order:

1. `git log` of the week repo. Find this week's work and the commits around a bug or a fix.
2. The week repo's README and notes. Find the exercise and what the student wrote about it.
3. The progress memo, if one exists. Find the step the student reached and what they confirmed.
4. `claude-mem`, only when it is installed. Search it for this week's sessions. If it is not installed, skip this step and say nothing about it (D15).

Write a short summary into the `Context notes` slot of `BRIEF.md`.
Use the facts to propose candidates in the decisions below.

## The six decisions

Settle these six decisions (D7). Each one has a slot with the same name in `BRIEF.md` (see `reference/brief-template.md`).

| # | Slot in `BRIEF.md` | What to settle | Who writes it |
|---|---|---|---|
| 1 | Conclusion and closing line | One sentence, lead-first, that goes on an early slide. Then the line that closes the talk. | The agent proposes candidates. The student chooses. |
| 2 | Story frame | 起承轉結 in 7 slides, or symptom → evidence → cause in 6 slides. | The agent proposes. The student chooses. |
| 3 | Slide theses | One sentence per slide. | The student writes. |
| 4 | Evidence list | Which real output goes on which slide, and how it was made. | The agent proposes. The student chooses. |
| 5 | Accent and style | The accent color and any style variation. | The agent proposes. The student chooses. |
| 6 | Terms to define on screen | Terms the audience may not know, each with a short on-screen definition. | The agent proposes. The student chooses. |

Rules for the decisions:

- The student writes each slide thesis. The agent does not write, rephrase, or edit a thesis. Copy it into `BRIEF.md` as written.
- You may ask questions that help the student write a thesis. Example: "이 슬라이드에서 청중이 가져갈 한 문장은?" Do not offer a thesis sentence as a candidate.
- For decisions 1, 2, 4, 5, and 6, give two or three candidates and one recommendation. Use the context notes as grounds.
- Evidence is real output only: a gcc, gdb, valgrind, or test run that you or the student ran. Do not invent output. Save it under `evidence/` in the deck folder.
- The order is a dependency order. Decision 1 comes before decision 3. Decision 2 fixes the slide count for decision 3. Decision 3 fixes the slides for decisions 4 and 6.

## Recording

- Write each settled decision into `BRIEF.md` immediately, in its slot. Do not wait for the end of the phase.
- Set `updated` and rewrite `Next action` in the same edit.
- Do not record the rejected candidates.
- A filled slot is settled. Do not ask about it again unless the student reopens it.
- Move `phase` to `build` only when the student confirms that all six decisions are done. All slots filled is not enough. Ask the student, and wait for the answer.

## Grilling rules

If the `grilling` skill is installed, use it to run the questions. Give it the six decisions above as the design tree.
If it is not installed, use the rules below. They are complete; you need no other file.

1. Map the decisions as a design tree. Each decision is a node. A node depends on the decisions that must be settled before it.
2. The frontier is every open decision whose prerequisites are all settled. Ask only frontier questions.
3. Ask the whole frontier in one round. Number each question. Give your recommended answer under each question.
4. Then stop and wait for the student's answers. Do not continue the round on your own.
5. After the answers, write the settled decisions into `BRIEF.md`. Then compute the new frontier and ask the next round.
6. A question that depends on another open question in the same round goes to a later round.
7. Facts are your job. Find them in the repo, the tools, and the context sources. Do not ask the student for a fact.
8. Decisions are the student's job. Put each decision to the student. Do not settle it yourself.
9. The phase is done when the frontier is empty and the student confirms the shared result.

Format each question like this:

```
**Q1 — <short title>**: <the question, with the candidates as a numbered list>

→ Recommended: <your answer and one line of grounds>
```

The student may answer by number, for example "1번" or "2, 3 수용". Accept that form.
