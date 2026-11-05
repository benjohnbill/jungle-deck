---
kind: case-record
case: week09-clean-code
status: A finished talk. A record of how it was planned, not rules to follow
---

# BRIEF — clean-code

## Grill

### Metadata

- What to present: 클린 코드가 왜 필요한가. 기존 핀토스 그래프 구조만으로는 뭐가 뭘 하는지 설명되지 않고, 남이 짠 코드를 받으면 실제 연산 단계까지 내려가야 한다. Before & After로 함수 이름만으로 추적되는 내 코드를 보여 주고, 우리가 만든 것의 전체 구조를 요약한다.
- Why: "남의 코드를 받으면 연산 단계까지 내려가야 이해됐고, 이름을 정리하니 이름만으로 추적됐다." 그리고 "다음주에 있을 agent를 활용하는 코드를 짤 때에도, 에이전트에게 이러한 clean code 기반의 룰을 명시해서 작성을 하면, 나중에 디버깅을 하거나 데이터 구조를 이해하는데 있어 크게 도움이 될 것이다." (the student wonders whether the second is the stronger one)
- The one line the audience should take away: 클린 코드는 전체 데이터 스트럭처가 어떻게 생겼는지를 파악하기 위해 필요하고, 특히 팀워크에서 상당히 유용하다. (The word stays; the overview slide shows the data structures as a diagram. Student said: "struct 슬라이드 같은건 없어. 1번으로 데이터 스트럭처 보여주는 것이 최선일 듯. diagram 형태로.")
- Slide count: 6 (the team's maximum). Team talk; the student presents last, 2 minutes: "그냥 내 얘기 하는 것과 다를바 없음."

### Story frame

- Structure: 도입 → 전개 → 전환 → 마무리, six slides (time is a guide): 01 도입, title, opening spoken, 15 s · 02 전개, the `do_mmap()` call graph shown roughly, 10 s · 03 전환, "받은 코드" (first-fault path, read node by node, "이거 뭔 소리 하는 지 알 수 있냐") beside "내 코드" (`do_mmap` tree, shown briefly), 25 s · 04 전환, name tree in four windows moving down, 45 s · 05 전환, the mmap() overview, 15 s · 06 마무리, conclusion in two lines, 10 s.
- Opening: Spoken only; the slide goes straight to the topic. The student mentions what the coach said last time about clean code: the student wondered what "클린 코드가 있어야 일을 하기 편하다" means, and the student thinks this use is exactly that.

### Title slide and closing line

- Title slide: "Clean Code를 어떻게 짜야 할까?" / "- 왜 Clean Code를 짜야 할까?" (student's edit, restored 2026-11-05). The accent on "Clean Code" is the student's. Head label: `Krafton Jungle · Week 09–10`.
- Closing line: Two lines on the last slide, the second in the accent. Line 1: `Agentic Coding에 들어가면, 모든 코드가 "남이 짠 코드"가 된다.` Line 2: `clean code를 시키는 능력이 필요하다.` Both are the agent's cut of the student's s6 script; the student can rewrite them on the page. They replace the data structure takeaway in Metadata.

### Slide theses

| # | Section id | Role | Thesis | Show |
|---|---|---|---|---|
| 01 | s1 | 도입, title | Clean Code를 어떻게 짜야 할까? | The title and the subtitle "- 왜 Clean Code를 짜야 할까?" (student's edit, 2026-11-05) |
| 02 | s2 | 전개 | 코드가 clean하지 않으면, 남이 짠 코드를 이해할 수가 없다 | The 44 real lines of `do_mmap()` before the refactor in an IDE look (syntax colors, line numbers, indent guides, function band) |
| 03 | s3 | 전환 | 진짜 팀원들끼리 맞추어야 하는 설계나 컨벤션은 이런 느낌 | No code at first: "동사 위치나 들여쓰기 같은 내용" alone. Press 1: it is struck through, and the heading appears. Press 2: the 44 lines appear, hold for a second, and fold to the 18 lines of `do_mmap()` in the IDE look |
| 04 | s4 | 전환 | "유저의 메모리 주소를 파일 페이지에 매핑해주기" (pinned; student said: "띄워둔 채로 설명하려고") | "mmap()은 무엇을 하는 함수인가?" alone in the middle. Press 1: the phrase takes the middle, under the question. Press 2: the phrase becomes the heading, and `mmap()`, `fd_to_file_mmap()`, `do_mmap()` appear across, one after another. Press 3: it turns down: a trident under `do_mmap()` with the tags "전처리 (validation check)", "핵심 로직", "후처리". Press 4: the `while` children. Press 5: the last level with brackets "파일 관련 부분" and "페이지 할당 부분" |
| 05 | s5 | 전환 | 함수를 따라가면 책임 소재가 보인다 | A table, one row per function: module, function, its responsibility in one phrase, and on the step the struct: `fd_to_file_mmap()` `int fd`, `do_mmap()` `spt`, `alloc_each_file_page()` `struct load_info`, `vm_alloc_page_with_initializer()` `struct page` |
| 06 | s6 | 마무리 | The closing line, two lines | The two lines |

Student said these theses stand in; the student writes the sentences on their own on the page.

Student said on the IDE look (2026-11-04): "최소한, IDE 처럼 함수 표시나, 뭔가 구분되는 표시같은게 있긴 해야 할 것 같아"; the bars on s3 had "직접 내용이 없으니까, 뭔가 아쉬움"; the 18-line after "좋음", "구분자는 필요".

Student said about s2 and s3 (2026-11-04), picking the code before the refactor: "2번이 사실 더 직관적으로 내 B/A를 보여주긴 하는데", "44줄 이라는 그 크기에 압도되기도 좋고". The first-fault staircase of "받은 코드" is off s3, because the student's script does not use it; `evidence/first-fault-path.txt` stays. The theses of s2 and s3 are the student's script words.

Student said earlier about s2 (2026-11-04): the module call counts "따로 노는 느낌이 아주 강하긴 해" and do not support s3 and s4; "설명을 기준으로 한다면, mmap()에 포커스를 두는게 맞아 보임". So s2 is the call graph of `do_mmap()`, and s3 names its path as the first fault of a mmap page.

Student said about s2 and s3 (2026-11-04): s2 and s3 looked the same, because s3 opened with the same 44 lines. The student picked the start with no code ("코드 없이 시작하는 것 좋아") and gave new scripts for both.

Student said after seeing the row boxes on s5 (2026-11-04): "너무 난잡한데", "인자를 하나하나 다 적는 느낌이라기 보다는, 책임 소재의 개념으로", "alloc_..with_initializer()는 page를 spt에 매핑하기". About s4: label the left of the core logic as "전처리(validation check)" and the right as "후처리"; the first screen runs across, "원래 화면은 가로 방향이 더 기니까". The agent wrote the phrases of s5 from the student's s4 script where it could: the student can ask for changes, because SVG text is locked.

Student said about s5 in the student's script (2026-11-04): "(5번 내용에서 sys_mmap()의 오른쪽에 int fd를 넣어주고, mmap() 옆에는 유저의 syscall 명령어를 넣어주면 그림이 예쁘긴 하겠다. 내용상 일치만 한다면)". Both are checked against the code: `lib/user/syscall.c:137`, `fd_to_file_mmap()`.

Student said earlier about s5 (2026-11-04): the data structure slide "따로 노는 경향이 있어". The data structures appear only "mmap()을 설명하는 사례로서": "overall architecture / flow chart(우리가 4번에서 제시하는 함수 흐름) / '거기에 사용되는 구조체'", in the last overview. `struct frame` and swap are off the slide, because the mmap() path does not touch them. The s5 thesis is the agent's proposal; the student can rewrite it on the page.

Student said after the first draft (2026-11-04): "글이 많거든", "내가 보여주고 싶은건 트리 구조 느낌이라니까". The text windows are replaced by this tree; names only. `remove_page_range()`, the failure paths, the local variables, and the reason for `record_page_cnt()` moved to the notes. `remove_page_range()` is off the s3 tree too, because it runs only on failure.

```
mmap()
└ fd_to_file_mmap()
  └ do_mmap()
    ├ is_valid_addr_and_length(), is_valid_offset(), is_page_range_unused()
    ├ alloc_file_page()
    │ ├ alloc_each_file_page()      (while)
    │ │ ├ register_memory_mapped_file()
    │ │ ├ set_load_info()
    │ │ └ vm_alloc_page_with_initializer()
    │ └ advance_page()
    └ record_page_cnt()
```

`sys_mmap()` is renamed `fd_to_file_mmap()` in the code (the student did it). The retrospective "SPT에 등록 (프레임은 첫 fault 때)" is not in the student's s4 script, so it is off the notes.

### Evidence list

| Slide | Evidence | File in `evidence/` | How it was made |
|---|---|---|---|
| s2 | `do_mmap()` before the refactor, 44 lines; line 40 does not compile (work in progress at that commit) | `do-mmap-before.txt` | `git show 3b53114^:pintos/vm/file.c` |
| s3 | `do_mmap()` before and after: 44 lines to 18 lines | `do-mmap-before.txt`, `do-mmap-after.txt` | `git show` of `pintos/vm/file.c`; the working tree of the student's branch after the student's rename |
| s4 | `do_mmap()` and its callees | `do-mmap-after.txt`; the callee names checked in `pintos/vm/file.c` | The working tree of the student's branch |
| s5 | The variables and structs per function | `data-structures.txt` | The working tree of the student's branch: `lib/user/syscall.c`, `userprog/syscall.c`, `vm/file.c`, `vm/vm.c`, and the headers |

No test counts on any slide. Student said: "테스트 결과 넣을 필요 없어. 어차피 다른 팀원이 현황 발표는 알아ㅓ 함."

### Terms to define on screen

| Term | On-screen definition | Slide |
|---|---|---|
| 없음 | Student's answer: none | |

### Script

s1 to s6: the student's script, in the page notes (2026-11-04). 이후 수정은 페이지에서.

## Design

- Source: the team's shared DESIGN.md (Plex Swiss Grid). Student said: "기존에 썼던 발표 포맷하고 똑같음".
- Tokens: `--paper: #ffffff` (neutral) · `--ink: #0a0a0a` (primary, the file's ink) · `--acc: #ff3300` · `--mut: #6b6b6b` (muted) · `--panel: #f7f7f5` (panel) · `--grid: #ebebeb` (grid). The same values as week08: the file's own values, not the mapping fallbacks. Fonts: `'IBM Plex Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif`; code `'IBM Plex Mono', 'IBM Plex Sans KR', monospace` (the week08 page and DESIGN.md; Korean in the slide 04 tree needs the second font).
- Accent: #ff3300
- Accent key: accent
- Code colors: code on s2 and s3 uses the student's Zed theme, read from `Zed/themes/xy-zed-orchid.json` (`XY-Zed Orchid Light`) and the overrides in `Zed/settings.json` (student said, 2026-11-04): function `#a63061`, keyword `#9230a6`, type `#a65430`, constant `#50384d`, comment `#856aa0` (4.29:1 on `--panel`, kept as in the theme), variable `#61485e`. Function names have a marker: `--acc` at 18% on `--panel`, 4.74:1 under the function color. The rest of the page keeps one accent.
- Figures: s4 and s5 use `artifact-diagramming` (student said), as node figures in inline SVG; s2 and s3 are inline SVG code. Tokens stay. `DESIGN.md` now says "draw structure as a figure, text is names only" instead of "code panels are the hero" (student said, 2026-11-04: a stopgap; the student fixes the file properly in a separate session).

## Revise

| Round | Date | What changed |
|---|---|---|
| 1 | 2026-11-04 | s4 opening added from the student's feedback: question, then the phrase in the middle, then the chain appears; steps renumbered 1 to 5 |
| 2 | 2026-11-04 | s2 and s3 code colors from the Zed theme, accent marker on function names, `struct` split into keyword and type |
| 3 | 2026-11-04 | s1 title and subtitle from the student; page title and description changed with them |
| 4 | 2026-11-04 | s5 box of `fd_to_file_mmap()` changed from `struct file` to `int fd` (student said) |
| 5 | 2026-11-04 | s5 column "구조체" became "바뀌는 값" (`before → after`, checked against the code), column "책임" became "책임 소재", rows appear top to bottom, the `struct load_info` row in accent (student picked option 1; "책임 소재" from the student) |
| 6 | 2026-11-05 | s1 title and subtitle from the student's restored edit; page title and og:title changed with them |
| 7 | 2026-11-05 | s2 heading on one line (student said); the counts "44줄" and "18줄" removed from s2 and s3 (student said: "라인 수가 중점이 아닌 것 같아서") |
| 8 | 2026-11-05 | s1 title on one line (student said). s5 column "바뀌는 값" replaced: back to "구조체", no argument conversions; press 1 shows `int fd → struct file` and `spt`, press 2 shows the split into 파일 (`struct load_info`) and 페이지 (`struct page → spt`). Student's reason: s5 explains 책임 소재 from s4; the split is inside `alloc_each_file_page()` in the code. One note line added for ▸2 |
| 9 | 2026-11-05 | s5 heading changed to "함수를 따라가면 책임 소재가 보인다" (student picked option 1 of 3); s5 figure and animation accepted by the student |
