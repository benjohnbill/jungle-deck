# Vague plan

A student with only a fuzzy idea. The skill must help the student sharpen that
idea, not swap it for a topic of its own choice.

## Sub-features

- `take-the-hunch`: the hunch is recorded as the topic seed.
- `help-inside`: candidates sharpen the hunch with facts from the repo.
- `offer-not-push`: a fact the student did not mention is offered once, as a question.

## How to get to it (user POV)

- The student types `/jdv:jungle-deck` and answers the opening question with a half-formed idea.

## Driving it with jdv.py

Persona card:

- Opening answer: "이번 주에 스택 쪽에서 뭔가 계속 막혔는데… 그거 얘기하면 좋을 것 같아요. 흐름은 아직 모르겠어요."
- When given candidates: pick the one closest to "막혔던 이유" and rewrite it lightly in your own words.
- Takeaway: "모르겠어요, 추천해 주세요". Slide count, save folder, story frame: accept the recommendation. Script: no.
- If asked "이런 것도 있었는데 넣을까요?": answer yes once, no after.

Steps:

1. `stage <scratch>/runs/vague-plan-<rev> <rev>`.
2. `turn <run> "/jdv:jungle-deck" --new`, then the opening answer above.
3. Answer from the card until "이 내용으로 디자인을 정할까요?"; stop there.

Pass predicates:

- `take-the-hunch`: the first candidates (quote them) are all about the stack problem; none is about another part of the week (the teammate's branch convention, for example).
- `help-inside`: the candidates or the recorded thesis cite a repo fact the student did not say (syscall, `rsp`, `pt-grow-stack`); quote the reply.
- `offer-not-push`: any new fact arrives as a question ("넣을까요?"), not as a settled slot. `BRIEF.md` `What to present` holds the student's rewrite.
- `context_reads_before_first_answer` is 0; `subagents_in_grill` is 0.

## Gotchas

- "흐름은 아직 모르겠어요" means the flow slot is open: the story frame round must still run and recommend one.
