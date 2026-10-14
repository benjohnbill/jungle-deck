---
scope: The personal settings file jungle-deck.local.md (SPEC D16) and the first-run questions that write it
authority: SPEC.md D15, D16, D20, D24. Key names here are a contract with scripts/publish.py and scripts/pull_edits.py; change them only together
status: revised 2026-10-15 (D16 keys, migration); unverified draft (D19). scripts/publish.py still reads pages_repo only; T18 (issue #18) moves it to pages_dir
---

# jungle-deck.local.md — template and first run

`jungle-deck.local.md` holds one student's personal settings. It lives in
the skill directory, next to `SKILL.md`. It is gitignored: never commit it,
never copy it into a save folder or a Pages repo.

Every student uses the same code path. The author also uses this file.

## When to read and write it

1. At the start of every call, read `jungle-deck.local.md` from the skill
   directory.
2. With no file, start the first run: run the Python check below, then
   ask the first-run questions, then write the file from the
   template. Do not start `grill` before the file exists.
3. A key that is missing (not in the file) is asked once when it is first
   needed, at the moment the "Asked or written" column names. Write the
   answer into the file at once.
4. An empty value `""` is a valid answer: apply the "If empty" meaning and
   the key is never asked again.
5. Change a value only when the student asks, or when a phase says so (the
   "Asked or written" column).

## File format

The file is YAML front matter, then optional prose. Scripts read only the
front matter. Values are plain strings. An empty string `""` means "not
set". Paths may start with `~`; expand `~` to the home directory before use.

## Fields

The scripts read these key names; the agent reads all of them. Do not rename them.

| Field | Key | Default | If empty | Asked or written |
|---|---|---|---|---|
| display name | `display_name` | `git config user.name`, offered at the first run | No speaker name on the title slide or the card. | First run. |
| study-notes site | `notes_url` | `""` | Context collection skips the notes site (D8). | First run. |
| DESIGN.md path | `design_md` | `""` | No personal style yet. `design` asks for a reference (D17). | `design` asks the accent and the style; `publish` can write a new DESIGN.md path (D14). |
| preferred accent | `accent` | `""` | No preference. `design` proposes accent candidates (D17). | `design`. |
| downloads folder | `downloads_dir` | The folder that `<python_cmd> scripts/downloads_dir.py` prints | `pull_edits.py` detects the folder on each run and prints a one-line hint. | The first time the export fallback runs (D11): offer the folder that `<python_cmd> scripts/downloads_dir.py` prints. If it exits non-zero (WSL with no answer), there is no default: ask for the folder. |
| Python command | `python_cmd` | The first command that passes the Python check | Run the Python check, then write the command it found. | The Python check. |
| current presentation | `current_brief` | `""` | Resume searches only the current directory (`reference/brief-template.md`). | Written when a presentation is created. |
| previous presentation | `prev_brief` | `""` | Context collection uses the last 7 days and has no last-week topic (D8). | Written when a presentation is created: it gets the old `current_brief` value. |
| Pages repo path | `pages_repo` | `""` | No publish target. `publish` stops at a finished local HTML and prints its path. No copy, no push, no card. | `publish`, when the student says yes to a separate deploy (D12). |
| Pages source folder | `pages_dir` | `<pages_repo>` (the repo root) | Use the default. | `publish`: read from `gh api repos/<owner>/<repo>/pages`, else asked once ("이 저장소는 어느 폴더가 배포돼요? (루트 / docs)"). |
| Pages URL base | `pages_url_base` | Derived from `pages_repo` (see "Pages" in SPEC.md) | Ignored when `pages_repo` is empty. Else use the default. | `publish`, after the student confirms the derived URL once. |
| card format | `card_format` | `builtin` | Use `builtin`. | Never asked; write `builtin`. |

### Field rules

- `display_name`: the speaker name on the title slide and in the card.
- `notes_url`: the URL of the student's study-notes site (a blog, a Notion
  page, a GitHub Pages site). If it cannot be read, ask the student to paste
  or export the page (D8).
- `design_md`: path to the student's DESIGN.md (Google Labs format).
- `accent`: one CSS color, for example `#d23c2c`, or a color name the
  student said.
- `downloads_dir`: the folder where the browser saves the page export
  (`Ctrl+S` without the revise server). On WSL it is the Windows downloads
  folder, seen through `wslpath`.
- `python_cmd`: the command that runs the scripts, for example `python3`,
  `python`, or `py -3`. Every script call in the reference files starts
  with `<python_cmd>`; put this value there.
- `current_brief`, `prev_brief`: absolute paths of BRIEF.md files. When a
  presentation is created, the old `current_brief` value moves to
  `prev_brief`, then `current_brief` gets the new path. `prev_brief` gives
  last week's topic and the start of the D8 window.
- `pages_repo`: a local clone of a GitHub Pages repository.
- `pages_dir`: the folder that GitHub Pages serves: `pages_repo` itself, or
  `<pages_repo>/docs`. The page copy goes to `<pages_dir>/study/weekNN/`
  when the week is known, else `<pages_dir>/study/` (D12).
- `pages_url_base`: the URL that serves `pages_dir`. It ends with `/`.
- `card_format`: `builtin`, or a path to a file that holds one card snippet
  with the same placeholders as the built-in card below.

### Built-in card (`card_format: builtin`)

`publish` inserts one card into `<pages_dir>/index.html`, only when the week
is known and the index holds card markup of this shape (D12). It drafts the
text from BRIEF.md and shows it to the student first.

```html
<a class="card" data-week="{week}" data-topic="{topic}" data-kind="deck" data-src="{src}" href="{deck_url}">
  <div class="t dh">{title}</div>
  <div class="d">{description}</div>
  <div class="m"><span class="b">발표 자료</span><span class="b wk">{week}주차</span><span>{meta}</span></div>
</a>
```

| Placeholder | Value |
|---|---|
| `{week}` | Week number without zero padding, for example `6` |
| `{topic}` | One `data-topic` value already used in the index (one topic per card). A new topic needs the student's approval and a title-color rule in the index CSS |
| `{src}` | Path of the page source file as the student names it, for example `my-repo/talks/<slug>/<slug>.html` |
| `{deck_url}` | The page URL from `pages_url_base` |
| `{title}` | The presentation title |
| `{description}` | Two or three sentences from the BRIEF.md title slide and metadata |
| `{meta}` | `weekN · 2분 발표` |

`publish.py` verifies the card only by a grep for `{deck_url}` in the live index.

## Python check

The scripts need Python 3.8 or later. Run this check on the first run,
when `python_cmd` is empty, or when the recorded command fails. A command
that works is not checked again.

1. Run each command with `--version`, in this order, and stop at the
   first one that prints `Python 3.8` or later: `python3`, `python`,
   `py -3`. On Windows, `python` can be a Microsoft Store stub that
   prints no version; treat it as a failure.
2. Write that command (without `--version`) to `python_cmd`.
3. If no command passes, tell the student Python 3.8 or later is
   required, and give the install source for their OS: python.org
   (Windows, macOS), Homebrew `brew install python` (macOS), or the
   system package manager, for example `sudo apt install python3`
   (Linux, WSL). Do not install Python yourself. Stop the phase until the
   student says Python is installed, then run the check again.

## First-run questions

Ask these two in one message, as a numbered list, with the default for
each. Both may be `""`: an answer like "없음" or "건너뛰기" writes `""`.
Every other key is asked later, when it is first needed.

| # | Question | Writes | Default answer |
|---|---|---|---|
| 1 | 발표 자료에 넣을 이름은 무엇인가요? | `display_name` | Your `git config user.name` |
| 2 | 공부 기록을 올리는 사이트가 있나요? 주소를 알려 주세요. | `notes_url` | 없음 |

## Migration

An existing file keeps working. Read the keys it has. A key that is not in
the Fields table, such as `last_brief` or another key from the 2026-10-07
format, is ignored: leave it in the file, never read it. A key from the
Fields table that is missing is asked once when it is first needed (see
"When to read and write it").

## Template

Write this file as `<skill dir>/jungle-deck.local.md`:

```yaml
---
display_name: ""
notes_url: ""
design_md: ""
accent: ""
downloads_dir: ""
python_cmd: ""
current_brief: ""
prev_brief: ""
pages_repo: ""
pages_dir: ""
pages_url_base: ""
card_format: builtin
---
```

Below the front matter, write one line: "Personal settings for jungle-deck.
Gitignored. Field meanings: reference/local-template.md."

## Example

One student's values after a few weeks. An example only, not defaults.

```yaml
---
display_name: 홍길동
notes_url: https://example.github.io/notes/
design_md: ~/my-pages/DESIGN.md
accent: ""
downloads_dir: ~/Downloads
python_cmd: python3
current_brief: ~/projects/week07/pintos-talk/BRIEF.md
prev_brief: ~/projects/week06/malloc-talk/BRIEF.md
pages_repo: ~/my-pages
pages_dir: ~/my-pages
pages_url_base: https://example.github.io/
card_format: builtin
---
```
