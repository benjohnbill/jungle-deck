# jungle-deck

A Claude Code skill that builds a 2-minute Krafton Jungle presentation
(발표 자료) as one HTML file. It runs in six phases:
`grill → design → build → revise → publish → done`. It keeps its state in a
`BRIEF.md` in the presentation's save folder, so you can stop and resume at
any time. The design is in [SPEC.md](SPEC.md).

## Requirements

- Claude Code on macOS, Windows, Linux, or WSL.
- Python 3.8 or later. The first run finds a working command (`python3`,
  `python`, or `py -3`). If none works, it tells you how to install
  Python for your OS and stops. It does not install anything.
- git.

Optional. Each one has a built-in fallback, so the skill works without it:

| Tool | With it | Without it |
|---|---|---|
| [frontend-slides](https://github.com/zarazhangrui/frontend-slides) skill | Style discovery in `design` | The copies in `vendor/frontend-slides/` |
| `grilling` skill | Runs the `grill` questions | Built-in question rounds |
| `gh`, logged in | Reads issues, PRs, and the Project board; finds the Pages source folder | Public repos only, through the GitHub REST API; no Project board; the skill asks for the Pages folder |
| `claude-mem` | One more context source in `grill` | Skipped |

## Install

macOS, Linux, WSL:

```bash
git clone https://github.com/benjohnbill/jungle-deck ~/.claude/skills/jungle-deck
```

Windows (PowerShell):

```powershell
git clone https://github.com/benjohnbill/jungle-deck "$HOME\.claude\skills\jungle-deck"
```

## First run

1. Open Claude Code in the repository you worked in this week.
2. Say "발표 자료 만들자" or type `/jungle-deck`.
3. The skill checks Python first. Then it asks two questions: the name to
   show on the presentation, and your study-notes site. Both may be
   empty. It writes the answers and the Python command to
   `jungle-deck.local.md` in the skill directory. This file is gitignored.
   Other settings are asked later, when a phase first needs them.
4. The skill asks "이번 주 발표 자료를 어디에 저장할까요?" (default:
   `<current directory>/<slug>/`), writes a `BRIEF.md` there, and the
   `grill` phase starts.

Later calls read `BRIEF.md` and resume at its phase. Say
"jungle-deck 이어서" to continue, or "발표 자료 게시" to publish. The old
phrases "발표 덱" and "덱 게시" still work.

## Workflow

Each phase ends only when you confirm it. The skill proposes 1–3 candidates
and recommends one; what it records is your pick or your rewrite.

### grill — the content

| The skill does or asks | You decide |
|---|---|
| Reads your own commits, your study notes, GitHub issues and PRs, and `claude-mem` (no questions yet) | — |
| Shows what it found and could not read; "이 로컬 저장소를 기준으로 보면 될까요?"; offers the team log | The source repo, more sources, anything else it should know |
| Candidates for the topic, your motive, the one takeaway line, the slide count (about 6 ± 2) | Each of the four |
| Story structure (오프닝 → 도입 → 전개 → 전환 → 마무리, or 증상 → 증거 → 원인) and the opening | Structure and opening |
| The title slide (the point, first) and the closing line | Both lines |
| One thesis sentence per slide | Each thesis |
| Which real output goes on which slide; re-runs the commands into `evidence/` | The evidence list |
| Terms the audience may not know | Terms and their on-screen definitions |
| "발표 스크립트를 먼저 만들까요?" | Yes: a full script draft to edit. No: light notes later |
| "이 내용으로 디자인을 정할까요?" | Move on to `design` |

### design — the style

| The skill does or asks | You decide |
|---|---|
| With a saved DESIGN.md: "이번에도 이 스타일로 갈까요?" | Reuse it, or pick a new style |
| "원하는 디자인 레퍼런스가 있어요? (사이트 URL, 이미지, DESIGN.md)" and "getdesign.md 레퍼런스 중에서 고를까요?" | A reference, a getdesign.md brand, or neither (then `frontend-slides` styles or presets) |
| Two or three previews in `previews/` | One preview |
| The accent with the DESIGN.md key it came from: "강조색은 `<color>`이고, DESIGN.md의 `<key>`에서 가져왔어요. 이 색으로 갈까요, 다른 색을 고를까요?" | Keep it or pick another; the first time, also whether to keep it for next time |
| "이 디자인으로 발표 자료를 만들까요?" | Move on to `build` |

### build — the first draft

| The skill does or asks | You decide |
|---|---|
| Writes `<slug>.html` from the template, your content, and your style; copies images into `<slug>.assets/` | — |
| Puts your script (or light notes) into the speaker notes | — |
| Starts a local server and gives you `http://127.0.0.1:<port>/<slug>.html` | — |
| Asks you to check the first draft | Move on to `revise` |

Keys in the page: `→` next, `N` notes, `E` edit, `Ctrl+S` save, `?` all
shortcuts. While editing, `Tab` opens the size buttons for the text you
picked (text size, box width). `R` reloads when the page asks for it.

### revise — the main loop

| The skill does or asks | You decide |
|---|---|
| — | Edit text, sizes, and notes in the page (`E`), then save (`Ctrl+S`) and say "저장했어, 봐줘" |
| Reads the save, shows changes that look accidental | Keep or undo them |
| Fixes layout, slide splits, and evidence around your words and sizes | A new slide's thesis (from its candidates) |
| Changes the page; the page asks you to press `R` | — |
| Never asks whether you are done | Say "발표 자료 게시" to move on to `publish` |

### publish — commit and deploy

| The skill does or asks | You decide |
|---|---|
| Lists `evidence/` files and any token-like strings (when the save folder is in a git repo) | Redact, leave out, or keep each hit |
| "이 발표 페이지를 따로 배포할 생각이 있어요?" | No (stop at the local HTML), GitHub Pages, or another host (you get the paths) |
| For Pages: your Pages repo path; the deployed folder (only when `gh` cannot read it); the page URL | Each of them, once; the next publish reuses them. A `gh-pages` branch source stops at the local HTML |
| Copies the page into the Pages repo; drafts an index card when your index has cards | The card text |
| Shows each repo and the files it will commit, the URL, and the card in one message: "커밋하고 푸시할까요?" | Commit and push, or not (one question); a yes commits and pushes with no second question |
| Waits until the live page answers and matches | — |
| Offers to save the style as DESIGN.md, or shows what changed against yours | New file, replace, no; or which changes to apply |
| Asks whether the presentation is done | `phase: done` |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| On WSL, the Windows browser cannot open `http://127.0.0.1:<port>/...` | `localhostForwarding=false` in `.wslconfig` | Remove that line and run `wsl --shutdown`. Or tell the skill and work without the server: open the page as a file; `Ctrl+S` exports it; the skill merges the export |
| "서버가 꺼져 있어요" in the page | The revise server stopped (for example, the Claude Code session ended) | Say "서버 다시 켜줘". Same address: press `Ctrl+S` again. New address: your unsaved edits stay on the old one; the failed save went to your downloads folder, and the skill merges it |
| The skill does not react after you save | The `Monitor` tool is not available in this session | Say "저장했어, 봐줘" after each save. This is the normal flow |
| "에이전트 수정과 겹쳐요" | You and the skill changed the same slide | Say "겹친 거 합쳐줘". Your words win |
| "저장이 안 됐어요 (HTTP 403)" | The page was not opened at the server address | Open the address the skill gave you. The failed save was exported to your downloads folder; tell the skill |
| "저장 안 된 편집이 있어요 — 그 뒤에 파일이 바뀌었어요" | The browser kept edits you never saved, and the file changed after them | Press "복원" |
| "에이전트 수정 뒤 내 저장 문구가 바뀌었어요" | A change by the skill replaced words or sizes you saved | Press "복원" to put your save back, or "그대로 두기" to keep the skill's version. Then tell the skill which one |
| "글이 상자를 넘쳐요" | Your text does not fit its box or its slide, often after a size step. In edit mode (`E`) the box is marked | Ask the skill to fix the layout. It keeps your words and sizes, or proposes a change |
| "에이전트가 슬라이드를 지웠어요" | A slide you saved is gone from the file | Ask the skill whether it meant to delete it. If not, it puts the slide back as it was before its edit |
| The live page check times out | GitHub Pages is still building | Ask the skill to check again later. Do not push again |

## Credits

Slide styles, the viewport base CSS, and the HTML template come from
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) by Zara
Zhang, under the MIT License. See `vendor/frontend-slides/SOURCE.md` for the
exact upstream commit.

## License

MIT. See [LICENSE](LICENSE).
