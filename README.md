<!-- readme: archetype=tool -->
# jungle-deck

이번 주 발표 내용을 정하는 일부터 2분짜리 HTML 발표 자료를 만들고 게시하는 일까지 돕는, 크래프톤 정글 학생용 Claude Code 스킬이에요.

Status: active

모든 단계를 실제 발표에서 돌려 봤어요. 완성 예시 보기:
- [Pintos 시스템 콜, 버전 Y](https://benjohnbill.github.io/jungle-deck/examples/pintos-syscall/deck-Y.html): 최근 업데이트를 반영한 프로토타입이에요. 도식마다 요점을 하나만 담았고, 스킬이 만드는 결과물에 가장 가까워요.
- [Pintos 시스템 콜, 버전 X](https://benjohnbill.github.io/jungle-deck/examples/pintos-syscall/deck-X.html): 최근 업데이트를 반영한 프로토타입이에요. 도식마다 내용을 자세히 담았어요.

실제 발표 사례:
- [함수에 들어가는 순간 배열이 아니다](https://benjohnbill.github.io/SW-AI-C/study/week04-array-in-c.html)
- [C에서 객체지향 프로그래밍하기](https://benjohnbill.github.io/study/week05/oop-in-c.html)
- [Typecasting - 컴파일러가 통과시키는 오류](https://benjohnbill.github.io/study/week06/bsize-cast.html)
- [PintOS 1주차 [Thread] · 9팀 발표](https://benjohnbill.github.io/study/week07/team9.html)
- [list에서 끝을 없앴더니, 분기가 사라졌다](https://benjohnbill.github.io/study/week07/circular-list.html)
- [PintOS 2주차 [User Programs] · 8팀 발표](https://benjohnbill.github.io/study/week08/team8.html)
- [1주일간의 8팀](https://benjohnbill.github.io/study/week08/p2-team-workflow.html)

## 시작하기
macOS, Linux, WSL:
```bash
git clone https://github.com/benjohnbill/jungle-deck ~/.claude/skills/jungle-deck
```
Windows (PowerShell):
```powershell
git clone https://github.com/benjohnbill/jungle-deck "$HOME\.claude\skills\jungle-deck"
```

이번 주에 작업한 저장소에서 Claude Code를 열고 "발표 자료 만들자"라고 말하세요.

## Map (파일 지도)
- `SKILL.md` (entry): 스킬의 시작점. `BRIEF.md`를 찾아 지금 단계의 규칙 파일로 넘겨요.
- `reference/`: 단계별 규칙, `BRIEF.md` 양식, 설정 양식.
- `templates/stage.html`: 발표 페이지의 틀과 실행 코드.
- `scripts/`: 수정 서버, 레이아웃 검사, 게시에 쓰는 스크립트.
- `vendor/`: 함께 배포하는 `frontend-slides`와 `diagram-design` 복사본.
- `docs/examples/`: 사람이 보는 예시 발표 자료. 스킬은 읽지 않아요.
- `cases/`: 완성한 발표별 `DESIGN.md`와 기록. 빠르게 참고할 디자인을 달라고 하거나 사례를 참고해 달라고 할 때만 스킬이 읽어요.
- `tests/`: 규칙 파일과 스크립트의 테스트. 스킬을 쓸 때는 필요 없어요.

## 다음에 읽을 것
- [`docs/MANUAL.md`](docs/MANUAL.md): 단계마다 스킬이 묻는 말과 내가 정할 것, 단축키, 문제 해결.
- `SPEC.md`: 설계와 결정 기록.
- 선택 (Optional):
  - `docs/adr/`: 주요 결정의 이유.
  - `AGENTS.md`: 이 저장소에서 일하는 에이전트의 규칙.

Agents: if a path named here does not exist, report it to the owner.

## 예시

버전 X와 Y는 최근 업데이트를 반영한 프로토타입이에요. 같은 Pintos 시스템 콜 발표를 두 가지 도식으로 그렸고, 차트 수치는 예시 데이터예요. 두 파일을 열면 화살표 키로 넘기고 `N` 키로 발표자 노트를 볼 수 있어요. 스킬은 이 예시들을 읽지 않아요.

## 준비물

- Claude Code (macOS, Windows, Linux, WSL).
- Python 3.8 이상. 처음 실행할 때 스킬이 쓸 수 있는 명령(`python3`, `python`, `py -3`)을 찾아요. 없으면 OS에 맞는 설치 방법을 알려 주고 멈춰요. 직접 설치하지는 않아요.
- git.

다음 도구는 없어도 돼요. 없으면 스킬이 대신할 방법을 써요.

| 도구 | 있으면 | 없으면 |
|---|---|---|
| [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 스킬 | `design`에서 스타일을 함께 찾아요 | `vendor/frontend-slides/` 복사본을 써요 |
| `grilling` 스킬 | `grill` 질문을 맡아요 | 내장 질문을 써요 |
| `gh` (로그인 상태) | 이슈, PR, Project 보드를 읽고 Pages 소스 폴더를 찾아요 | 공개 저장소만 GitHub REST API로 읽어요. Project 보드는 못 읽고, Pages 폴더는 직접 물어요 |
| `claude-mem` | `grill`에서 읽을 자료가 하나 늘어요 | 건너뛰어요 |
| Chrome, Chromium, Edge (WSL에서는 Windows의 Edge나 Chrome도 돼요) | `build`와 `revise`에서 레이아웃을 검사해요 | 건너뛰어요. 페이지를 직접 확인하세요 |

## 처음 실행할 때

1. 이번 주에 작업한 저장소에서 Claude Code를 열어요.
2. "발표 자료 만들자"라고 말하거나 `/jungle-deck`을 입력해요.
3. 스킬이 먼저 Python을 확인하고 두 가지를 물어요. 발표 자료에 표시할 이름과 공부 노트 사이트예요. 둘 다 비워 둘 수 있어요. 다른 설정은 어떤 단계에서 처음 필요할 때 물어요.
4. 스킬이 "이번 주 발표 자료를 어디에 저장할까요?"라고 물어요. 기본값은 `<현재 폴더>/<slug>/`예요. 그 폴더에 `BRIEF.md`를 만들고 `grill` 단계를 시작해요.

스킬은 `grill → design → build → revise → publish → done` 순서로 움직이고, 진행 상태를 `BRIEF.md`에 남겨요. 그래서 언제든 멈췄다가 이어갈 수 있어요. 각 단계에서 무엇을 묻는지는 `docs/MANUAL.md`에 있어요.

이어서 하려면 "jungle-deck 이어서"라고 말하고, 게시하려면 "발표 자료 게시"라고 말하세요. 예전 표현인 "발표 덱"과 "덱 게시"도 그대로 돼요.

## 설정

설정은 `~/.config/jungle-deck/jungle-deck.local.md`에 저장돼요. 스킬 폴더 밖에 있어서 설정을 저장할 때 권한을 묻지 않아요. 환경 변수 `JUNGLE_DECK_CONFIG`에 경로를 지정하면 그 파일을 써요.

이미 설치했다면 스킬 폴더에서 `git pull origin main`을 실행해 업데이트하세요. 스킬 파일을 직접 고쳤다면 Git이 거부하니, 먼저 `git stash`를 실행하고 업데이트 뒤에 `git stash pop`을 실행하세요.

## 한계

- 도식은 순서도, 시퀀스, 상태 전이, 타임라인, 트리, 계층, 막대 차트의 일곱 가지예요.
- 도식 하나에는 노드, 행, 막대를 6개까지, 넘기는 단계를 4개까지 담아요. 더 필요하면 슬라이드를 나눠요.
- 편집 모드(`E`)에서는 도식 안의 글자를 고칠 수 없어요. 스킬에게 바꿀 내용을 말하세요.
- GitHub Pages 소스가 `gh-pages` 브랜치이면 게시는 로컬 HTML에서 멈춰요.

## 크레딧

- 슬라이드 스타일, 뷰포트 기본 CSS, HTML 템플릿: Zara Zhang의 [frontend-slides](https://github.com/zarazhangrui/frontend-slides), MIT 라이선스. 가져온 커밋은 `vendor/frontend-slides/SOURCE.md`에 있어요.
- 도식 규칙과 검사 스크립트: Cathryn Lavery의 [diagram-design](https://github.com/cathrynlavery/diagram-design), MIT 라이선스. 가져온 커밋과 고친 내용은 `vendor/diagram-design/SOURCE.md`에 있어요.

## 라이선스

MIT. [LICENSE](LICENSE)를 보세요.
