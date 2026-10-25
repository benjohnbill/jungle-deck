---
scope: The grill phase (SPEC D7, D8): the opening question, the meta round, scoped context collection, the check-in, the grill rounds, the proposal rule, inline grilling
authority: SPEC.md D7, D8, D10, D15, D22; docs/adr/0001-ask-before-collecting-context.md. tests/test_grill_reference.py checks the rules here; slot names follow reference/brief-template.md
status: revised 2026-10-25; unverified draft (D19)
---

# Grill phase

The `grill` phase settles the content of one presentation (D7).
It starts when `BRIEF.md` has `phase: grill`, or when no `BRIEF.md` exists (D6).
It ends when the student answers yes to "이 내용으로 디자인을 정할까요?".

Read `reference/context.md` first. Its rows are defaults for every Jungle talk, not questions.

The student leads. The skill helps the student present; it does not choose the talk for the student.

## Proposal rule

This rule holds for every slot in this phase, and for a new or split slide in `build` and `revise` (D7).

- The student's draft comes first. A slot that the student filled is refined, not replaced. Candidates are variations inside the student's draft.
- Only an open slot gets 1–3 candidates, grounded in the context notes or in what the student said; recommend one, with one line of grounds.
- Never propose another topic or another flow than the student's.
- A fact from collection that the student did not mention: offer it once, in one line: "이런 것도 있었는데 넣을까요?".
- The recorded text is the student's pick or rewrite. Record it as the student gave it.

## Context collection

Run this only after the topic is known (Rounds, item 2), never before the opening question (D8).
Facts are your job: find them yourself. Collect in this session; use no subagents.

Keep it scoped to the topic: read only the commits, files, issues, and outputs that bear on it. Do not read every file that the window's commits touched.

`source_repo` in the BRIEF front matter is the git repo where the skill was called.
It can differ from the save folder. If it is empty (the skill was called outside a git repo), skip the git sources and ask for the repo path in the check-in.

Read the sources in this order:

1. **Own commits.** `git -C <source_repo> log --author=<git config user.email> --since=<window start> --stat`. The window starts at `created` of the BRIEF at `prev_brief` in `jungle-deck.local.md`. With no `prev_brief`, the window is the last 7 days. From the list, pick the commits on the topic, and read their files around each bug or fix.
2. **Study notes.** The site at `notes_url` in local.md. Skip it when the value is `""`. When the key is missing, ask for it once in the check-in and write the answer to local.md (D16). If you cannot read the page (for example a private Notion page), ask the student in the check-in to paste or export it.
3. **GitHub, with `gh`.** When `gh auth status` succeeds: the repo's issues, PRs, and Project board, on the topic.
4. **GitHub, without `gh`.** For a public repo: issues and PRs through the unauthenticated REST API (`https://api.github.com/repos/<owner>/<repo>/issues`, 60 requests per hour). The Project board needs `gh` (GraphQL requires auth); skip it.
5. **Fork parent.** When the repo is a fork (`parent` in `gh repo view --json parent`, or in `GET /repos/<owner>/<repo>`), read the parent's issues on the topic too.
6. **claude-mem**, only when it is installed. Search it for this window's sessions, then fetch only the observations that match the topic. If it is not installed, skip it and say nothing (D15).

Write a short summary into the `Context notes` slot of `BRIEF.md`: what was found, and what could not be read.

**Check-in message.** Send it in the same round as the metadata questions (Rounds, item 3). It holds:

- What was found, per source, and what could not be read, with the reason.
- The `source_repo` path and "이 로컬 저장소를 기준으로 보면 될까요?".
- "본인 커밋만 봤어요", with an offer to read the team log (the same `git log` without `--author`).
- Whether other sources exist, and whether there is more the agent should know.

## Rounds

Run these in order. Each item is a round; wait for the student's answers before the next one. Items 3–9 fill the `BRIEF.md` slots of the same name (see `reference/brief-template.md`).

1. **Opening question**, before any context is read. Ask only this:
   "이번 주에 발표하고 싶은 아이템이나, 대략 생각해 둔 흐름이 있어요? 없으면 '없어요'라고 해 주세요."
2. **The topic.**
   - The student has an item or a flow: write what the student said into the `What to present` line, and into the structure or the takeaway line when the answer covers them. Then run "Context collection".
   - The student says "없어요": read no context. Run the meta round, two steps. Give no recommended answer in either step: you know nothing yet that could ground one.
     1. One round of three recall questions, numbered. Add "답하기 쉬운 것만 답해도 돼요".
        - 이번 주에 시간을 가장 많이 쓴 세부 과제는 뭐였어요?
        - 가장 고민한 영역은 어디였어요?
        - 이번 주에 얻고 싶었던 능력이나 지식은 뭐였어요?
     2. One pick question: "2분 동안 사람들에게 보여 주고 싶은 것은 뭐예요?", with 1–3 candidates made from the student's own answers. The pick goes into the `What to present` line. Then run "Context collection".
3. **Metadata**, in the same round as the check-in. Ask only the items that are still open:
   - Why: the student's motive.
   - The one line the audience should take away. It steers the grilling; it need not appear on a slide.
   - Slide count: propose the number from the Time row of `reference/context.md`.

   If the check-in answer changes the sources (another repo, the team log, a new source, pasted notes), collect again on the same topic before you record the metadata.
4. **Story frame**, as two questions in one round. A frame fixes no slide count. A flow that the student gave in item 1: confirm it in the frame's words; it is not asked again.
   - Structure: 오프닝 → 도입 → 전개 → 전환 → 마무리 (storytelling; recommend it), or 증상 → 증거 → 원인.
   - Opening: common ground, which may link to last week's topic (read the BRIEF at `prev_brief`), or a plain topic introduction with the student's motive.
5. **Title slide and closing line.** The title slide states the point, lead-first. Then the line that closes the talk.
6. **Slide theses.** One sentence per slide, under the proposal rule.
7. **Evidence list.** Which real output goes on which slide, and how it was made. Follow the Evidence row of `reference/context.md`. Re-run each command in `source_repo` and save its output under `<save folder>/evidence/`.
8. **Terms to define on screen.** Terms the audience may not know, each with a short on-screen definition.
9. **Script**, optional. Ask "발표 스크립트를 먼저 만들까요?".
   - Yes: draft a full per-slide script that tells the story. A 2-minute speaking length (about 600–700 syllables) is guidance only (D10). Store the student's version in the `Script` slot.
   - No: write `없음 — build가 가벼운 노트를 씀` in the slot.
10. Ask "이 내용으로 디자인을 정할까요?". Move `phase` to `design` only when the student confirms.

A filled slot is settled. Skip its round unless the student reopens it.

## Recording

- Write each settled slot into `BRIEF.md` immediately.
- Set `updated` and rewrite `Next action` in the same edit.
- Leave the other candidates out of `BRIEF.md`.

## Grilling rules

If the `grilling` skill is installed, use it to run the questions. Give it the rounds above as the design tree.
If it is not installed, use the rules below. They are complete; you need no other file.

1. Map the rounds as a design tree. Each slot is a node. A node depends on the slots settled before it in the round order.
2. The frontier is every open slot whose prerequisites are all settled. Ask only frontier questions.
3. Ask the whole frontier in one round. Number each question. Give your recommended answer under each question. The meta round (Rounds, item 2) is the one exception: it has no recommended answer.
4. Then stop and wait for the student's answers.
5. After the answers, write the settled slots into `BRIEF.md`. Then compute the new frontier and ask the next round.
6. A question that depends on another open question in the same round goes to a later round.
7. Decisions are the student's job. Put each one to the student under the proposal rule.
8. The phase ends at round 10 above.

Format each question like this:

```
**Q1 — <short title>**: <the question, with the candidates as a numbered list>

→ Recommended: <your answer and one line of grounds>
```

The student may answer by number, for example "1번" or "2, 3 수용". Accept that form.
