# Clear plan

A student who already knows the topic and the flow. The skill must keep both,
read only what supports them, and propose only inside the student's draft.

## Sub-features

- `opening-first`: the first reply asks for the student's item or flow, and no context is read before the answer.
- `keep-topic`: the recorded `What to present` and story structure are the student's.
- `scoped-collection`: collection reads the commits on the topic, not the week at large.
- `draft-first`: any candidates are variations of the student's lines.

## How to get to it (user POV)

- The student types `/jdv:jungle-deck` in the repo of the week and answers the opening question with a plan.

## Driving it with jdv.py

Persona card (answer only from this):

- Topic: "syscall 안에서 스택 성장이 실패한 버그" (the stack-growth bug of this week).
- Flow: 증상 (pt-grow-stack이 syscall에서만 실패) → 원인 (intr_frame의 rsp가 커널 스택) → 수정 (진입 때 user rsp 저장) → 배운 점.
- Takeaway: "fault 주소는 어느 스택 기준인지부터 확인하자".
- Slide count: whatever is proposed. Save folder: the default.
- Script: no. Design: pick the first preview, keep the accent.

Steps:

1. `stage <scratch>/runs/clear-plan-<rev> <rev>`.
2. `turn <run> "/jdv:jungle-deck" --new`. Answer setup questions (save folder) with the default.
3. Answer the opening question with the topic and the flow in one message.
4. Answer each round from the card until "이 내용으로 디자인을 정할까요?". Answer "네" and stop when the design phase starts.

Pass predicates:

- `opening-first`: the first skill question asks for an item or a flow (quote it), and `context_reads_before_first_answer` is 0 in `measure_run.py` of the first session.
- `keep-topic`: `BRIEF.md` `What to present` holds "스택 성장" or "syscall", and the story structure is 증상 → 증거/원인 order or the card's own flow. No reply proposes a different topic or flow (quote any that does: FAIL).
- `scoped-collection`: no `Read` of `CONVENTION.md` (the teammate's unrelated file); `subagents_in_grill` is 0.
- `draft-first`: each candidate list in the replies contains the card's words or a close rewrite (quote the lists).

## Gotchas

- The old revision (before 2026-10-25) collects first and proposes topics first. On that revision `opening-first` and `keep-topic` are expected to FAIL; that is the baseline, not a broken run.
- The check-in round mentions "본인 커밋만 봤어요"; answer "네, 이 저장소 기준이에요".
