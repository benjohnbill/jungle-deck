# No plan

A student with no item and no flow. The skill must ask about the student's week
before it reads anything, and build the topic candidates from the answers.

## Sub-features

- `no-read`: nothing is read after "없어요" until the topic is picked.
- `recall-round`: three recall questions in one round, with no recommended answers.
- `pick-round`: one pick question, with candidates made from the student's answers.

## How to get to it (user POV)

- The student types `/jdv:jungle-deck` and answers the opening question with "없어요".

## Driving it with jdv.py

Persona card:

- Opening answer: "없어요".
- Most time: "스택 성장 테스트가 계속 실패해서 그거 붙잡고 있었어요".
- Hardest: "syscall 중에 난 page fault라는 걸 알아채는 거".
- Wanted to learn: "커널이 유저 스택을 어떻게 다루는지".
- Pick: the candidate closest to the syscall stack bug.

Steps:

1. `stage <scratch>/runs/no-plan-<rev> <rev>`.
2. `turn <run> "/jdv:jungle-deck" --new`, then "없어요".
3. Answer the recall round in one message, then the pick. Continue until the check-in round, then stop.

Pass predicates:

- `no-read`: `measure_run.py` on the session lists no context read (git log, Read of repo files) between the "없어요" turn and the pick turn. Use the tool-call order in the transcript; quote the first context read and the turn it follows.
- `recall-round`: one reply holds the three questions (quote them) and "답하기 쉬운 것만 답해도 돼요", with no "Recommended"/"추천" line under them.
- `pick-round`: the next reply asks "2분 동안 사람들에게 보여 주고 싶은 것" with 1–3 candidates; each uses words from the recall answers (quote them).

## Gotchas

- `context_reads_before_first_answer` counts reads before "없어요" only. The `no-read` window runs to the pick, so read the transcript order for it.
