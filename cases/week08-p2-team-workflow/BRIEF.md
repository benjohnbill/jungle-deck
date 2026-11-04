---
kind: case-record
case: week08-p2-team-workflow
status: A finished talk. A record of how it was planned, not rules to follow
---

# BRIEF — p2-team-workflow

## Grill

### Metadata

- Format: team talk, as in week07. The student covers the team's way of working and its result, with some of the student's own story. Speaking time 2 min 20 s.
- Title (student's): "1주일간의 8팀" — subtitle "Pintos Userprog".
- What to present: the team's week in time order, split by date (about two slides per date). Close with the student's own "내가 피상적이었다" as regret and resolve: work harder next week.
- Why: to show how the team collaborated, and how the student built the tools and ran the process for the team's collaboration.
- Student's view (steers the takeaway): the student considers the team a model case; the team's practice — exactly, the tools and system the student built — is the method or tool the audience can take away.
- The one line the audience should take away: "누가 짠 코드든 합칠 수 있게: 같은 컨벤션, 같은 테스트 명령, 같은 보드." The student has much to say on it. The student's regret also grew from it: "팀적으로 결과가 잘 나오고 있는 것 같은데, 내 이해는 따라가지 못하는 것 같다".
- Slide count: 7 + title = 8, in four date blocks: 목·금 2 (principles and convention, quiz), 토 2 (re-split, tools), 월 1 (deadline merge), 화·수 2 (split work and all pass, the blank-fill regret and resolve). Real time per slide follows weight and the student's emphasis, not an even split.

### Story frame

- Structure: time order by date block (목·금 → 토 → 월 → 화·수).
- Opening: link to last week. After all of last week's talks, the coach said publicly that teams should settle a convention in advance; one team's talk also said a convention seemed needed. "저희는 첫날 그걸 만들었습니다" → the 목 block.

### Title slide and closing line

- Title slide: "1주일간의 8팀" / "Pintos Userprog" + lead line "누가 짠 코드든 합칠 수 있게: 컨벤션 · `ptest` · 보드"
- Closing line: "누가 짠 코드든 합칠 수 있었습니다. 하지만 팀적인 통일과 개인의 이해도는 완전히 다른 영역이었습니다. 스스로가 부족했습니다. 다음주에는 원리와 실패 원인을 모두 명료하게 설명할 수 있도록 공부하려고 합니다."

### Slide theses

| # | Section id | Role | Thesis |
|---|---|---|---|
| 01 | s1 | Title | 1주일간의 8팀 — Pintos Userprog / 누가 짠 코드든 합칠 수 있게: 컨벤션 · `ptest` · 보드 |
| 02 | s2 | 목 | 지난주 코치님 말씀대로, 첫날 나누는 원칙과 컨벤션부터 깔았다. |
| 03 | s3 | 금 | 개념은 쪽지 시험으로 점검하고, 모르는 건 칠판에서 같이 풀었다. (Do not show "the student solved only 3 of 12": student said it is a different point from the closing's 부족함.) |
| 04 | s4 | 토 | 첫 PASS에 필요한 것이 보이자 다시 나눴고, 합칠 때는 AI가 컨벤션을 첫 기준으로 골랐다. |
| 05 | s5 | 토~월 | 테스트를 돌려야 해서 도구를 만들었다: 명령 한 번에 26초, 보드는 10초마다. |
| 06 | s6 | 월 | 월요일 마감 merge에서 내 fork·wait는 남지 않았지만, 컨벤션 덕에 바로 읽혔다. |
| 07 | s7 | 화·수 | 기능 단위로 나눠 합쳤고, 수요일 저녁 96개를 통과했다. |
| 08 | s8 | 마무리 | 팀은 합쳐졌지만 내 이해는 따라가지 못했다 → 빈칸 세션 → closing line. |

### Evidence list

| Slide | Evidence | File in `evidence/` | How it was made |
|---|---|---|---|
| s2 | Day-1 whiteboard (cropped: no "3시간 이상") | `whiteboard-day1.jpg` | student's photo IMG_8052.jpg |
| s2 | #104: 18/95 before and after the format | `pr-104.json` | `gh pr view 104 --json …` |
| s3 | Concept quiz page | `quiz-1.png`, `quiz-2.png` | student's screenshots |
| s4 | Plan page "나눈 기준" (cropped: 각자 and 분업 only, no "이음매") | `plan-page-criteria.png` | student's screenshot |
| s4 | #105 pick table, args/exit FAIL 6/6 → PASS 6/6; 4 AI criteria | `pr-105.json`; `../research/C-git-timeline.md` | `gh pr view 105`; transcript per research C |
| s5 | Plan page board (stands in for the video) | `plan-page-board.png` | student's screenshot |
| s5 | #107: 26 s, 95 results | `pr-107.json` | `gh pr view 107` |
| s6 | #108 source table | `pr-108.json` | `gh pr view 108` |
| s6 | #110 renames by rule (C4, C2) | `pr-110.json` | `gh pr view 110` |
| s7 | develop merges and dates; main merges | `develop-merges.txt`, `main-first-parent.txt` | `git log --first-parent origin/develop --merges` (KST) |
| s7 | 18/95 (#104), 46/95 (#108, notes/p2-debug.md), 50/95 (#110), 73/96 (#113), 94/96 at TIMEOUT 60 → 96 at 600 (#118) | `pr-*.json` | PR bodies |
| s8 | rewrite/fwe log | `rewrite-fwe-log.txt` | `git log rewrite/fwe --not origin/develop` (KST) |

### Terms to define on screen

| Term | On-screen definition | Slide |
|---|---|---|
| `ptest` / `pcheck` | 팀 테스트 명령 / 결과를 분업표에 반영 | s5 |
| icount | QEMU 가상 시계 모드: 테스트 17~25배 빠름 | s5 |
| develop | 매일 합치는 공용 브랜치 | s7 |

Student (2026-10-22): never use the word "이음매" (the student says it aloud; it reads AI-like). Board 6 → just "GitHub Project", and it is not a talking point: the live HTML page did that job.

### Script

build에서 노트로 옮김 — 이후 수정은 페이지에서

## Design

- Source: the student's own DESIGN.md (Plex Swiss Grid; same as week07, and the teammates built their HTML from it)
- Tokens: `--paper: #ffffff` (neutral) · `--ink: #0a0a0a` (primary, the file's ink) · `--acc: #ff3300` · `--mut: #6b6b6b` (muted) · `--panel: #f7f7f5` (panel) · `--grid: #ebebeb` (grid). The student chose the file's own panel/grid/ink values over the mapping fallbacks. Fonts: `'IBM Plex Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif`; code `'IBM Plex Mono', monospace`.
- Accent: #ff3300 (same as the team's decks, for unity)
- Accent key: accent

## Revise

| Round | Date | What changed |
|---|---|---|
| 1 | TBD | TBD |
