# Ask the student before collecting context

Decided 2026-10-25 by the author, in a grilling session on two pieces of
user feedback. SPEC D7, D8, D9, D11, D27. Tickets T34–T38.

## Context

The 2026-10-15 design ran context collection first in `grill`: own commits
and every file they touched, notes, issues, PRs, the fork parent, and
claude-mem. Then it proposed 2–3 topics as "맥락 기준 추천". Students said
two things:

1. "내가 발표 주제나 흐름을 제시하기 전에 자료 조사하고 추천하는 게 싫다. 도움을
   주는 녀석이지, 강요하는 스킬이 아니면 좋겠다."
2. "사용 token 양이 너무 많다."

A measured run (week08, 2026-10-21) used 26.49M cache-read tokens in the
main session over 130 turns, plus 13.19M in five grill subagents. Build (45
turns) and revise (36 turns) were screenshot-and-fix loops. Skill docs and
`stage.html` were about 22K tokens of payload, a small share.

## Decision

- `grill` starts with one open question: does the student have an item or
  a flow? No context is read before the answer.
- An item or a flow: record it as settled, then collect context scoped to
  that topic. The agent never proposes another topic or flow.
- "없어요": a meta round with no recommended answers. Three recall
  questions in one round, then one pick question with candidates made from
  the student's answers.
- Proposal rule: the student's draft first; candidates are variations
  inside it. Only an open slot gets candidates from the context.
- No subagents in context collection.
- Build runs one shipped layout check, then the student previews the page.
  Revise uses the server path by default; the student makes text and
  position edits.
- One suggested session break, at `design` → `build`.

## Consequences

- A student with no idea answers four questions before seeing any
  candidate. That is accepted: the questions are about the student, not
  the repo.
- The layout check needs a headless browser. Without one, the check is
  skipped and the student preview is the check (D15).
- Rejected: collect first and hide the result (same token cost); split the
  session at every phase (too many breaks for the student).
