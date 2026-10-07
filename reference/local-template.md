---
scope: The personal settings file jungle-deck.local.md (SPEC D16) and the first-run questions that write it
authority: SPEC.md D15, D16, D20. Key names here are a contract with scripts/publish.py and scripts/pull_edits.py; change them only together
status: draft 2026-10-07
---

# jungle-deck.local.md — template and first run

`jungle-deck.local.md` holds one student's personal settings. It lives in
the skill directory, next to `SKILL.md`. It is gitignored: never commit it,
never copy it into a week repo or a Pages repo.

Every student uses the same code path. The author also uses this file.

## When to read and write it

1. At the start of every call, read `jungle-deck.local.md` from the skill
   directory.
2. If the file is missing, run the Python check below, then ask the
   first-run questions. Then write the file from the template. Do not
   start `grill` before the file exists.
3. If a key is missing or empty, apply its "If empty" meaning from the
   Fields table. Do not ask again for an empty key; an empty value is a
   valid answer.
4. Change a value only when the student asks, or when a phase says so
   (D14: `publish` can record a new `design_md` path).

## File format

The file is YAML front matter, then optional prose. Scripts read only the
front matter. Values are plain strings. An empty string `""` means "not
set". Paths may start with `~`; expand `~` to the home directory before use.

## Fields

The scripts read these key names; the agent reads `python_cmd`. Do not rename them.

| Field | Key | Default | If empty |
|---|---|---|---|
| display name | `display_name` | `git config user.name` | Use the default. |
| week-repo root | `week_repo_root` | Parent directory of the current week repo (`git rev-parse --show-toplevel`, then `..`) | Use the default. |
| Pages repo path | `pages_repo` | `""` | No publish target. `publish` stops at a finished local HTML: commit in the week repo only, then print the local file path. No copy, no push, no card. |
| Pages URL base | `pages_url_base` | `https://<owner>.github.io/`, with `<owner>` from the `origin` remote of `pages_repo` | Ignored when `pages_repo` is empty. Else use the default. If no default can be made, ask once. |
| card format | `card_format` | `builtin` | Use `builtin`. |
| DESIGN.md path | `design_md` | `""` | No personal style yet. `build` runs `frontend-slides` style discovery (D17). `publish` offers to extract a DESIGN.md from the deck and record its path here (D14). |
| preferred accent | `accent` | `""` | No preference. `grill` proposes accent candidates and the student picks one (D7 item 5). |
| downloads folder | `downloads_dir` | The folder that `<python_cmd> scripts/downloads_dir.py` prints | `pull_edits.py` detects the folder on each run and prints a one-line hint. |
| Python command | `python_cmd` | The first command that passes the Python check | Run the Python check, then write the command it found. |

### Field rules

- `display_name`: the speaker name on the title slide and in the card.
- `week_repo_root`: the directory that holds the `weekNN/` repos. The skill
  finds the week repo under it when the current directory is not a week repo.
- `pages_repo`: a local clone of a GitHub Pages repository. The deck copy
  goes to `<pages_repo>/study/weekNN/<deck-slug>.html` (D12).
- `pages_url_base`: the URL that serves the root of `pages_repo`. It ends
  with `/`. Deck URL = `<pages_url_base>study/weekNN/<deck-slug>.html`.
- `card_format`: `builtin`, or a path to a file that holds one card snippet
  with the same placeholders as the built-in card below.
- `design_md`: path to the student's DESIGN.md (Google Labs format).
- `accent`: one CSS color, for example `#d23c2c`, or a color name the
  student said.
- `downloads_dir`: the folder where the browser saves the deck export
  (Ctrl+S in revise). On WSL it is the Windows downloads folder, seen
  through `wslpath`.
- `python_cmd`: the command that runs the scripts, for example `python3`,
  `python`, or `py -3`. Every script call in the reference files starts
  with `<python_cmd>`; put this value there.

### Built-in card (`card_format: builtin`)

`publish` inserts one card into `<pages_repo>/index.html`. It drafts the
text from BRIEF.md and shows it to the student first.

```html
<a data-week="{week}" data-topic="{topic}" class="card two" href="{deck_url}">
  <div class="t dh">{title}</div>
  <div class="d">{description}</div>
  <div class="m">{meta}</div>
</a>
```

| Placeholder | Value |
|---|---|
| `{week}` | Week number without zero padding, for example `6` |
| `{topic}` | Topic label of that week's group in the index |
| `{deck_url}` | The deck URL from `pages_url_base` |
| `{title}` | The deck title |
| `{description}` | Two or three sentences from the BRIEF.md conclusion |
| `{meta}` | `weekN / <exercise path> · 2분 발표` |

If `index.html` has no card markup that matches this shape, show the
drafted card and ask the student where to put it. `publish.py` verifies
the card only by a grep for `{deck_url}` in the live index.

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

Ask these in one message, as a numbered list. Show the default for each.
The student may answer by number, or answer "기본값" to take all defaults.

| # | Question | Writes | Default answer |
|---|---|---|---|
| 1 | What name goes on your slides? | `display_name` | Your `git config user.name` |
| 2 | Where are your `weekNN/` repos? | `week_repo_root` | The parent directory of the current week repo |
| 3 | Do you have a local clone of a GitHub Pages repo? Give its path. | `pages_repo` | No (publish stops at a local HTML file) |
| 4 | Do you have a DESIGN.md for your decks? Give its path. | `design_md` | No (first deck runs style discovery) |
| 5 | Do you want one accent color on every deck? | `accent` | No (pick one per deck in grill) |
| 6 | Where does your browser save downloads? | `downloads_dir` | The folder that `<python_cmd> scripts/downloads_dir.py` prints. If it exits non-zero (WSL without an answer), there is no default: ask for the folder |

Do not ask for `pages_url_base` when the default works. Do not ask for
`card_format`; write `builtin`. Ask for `pages_url_base` once only when
`pages_repo` is set and its `origin` remote is not on github.com.

## Template

Write this file as `<skill dir>/jungle-deck.local.md`:

```yaml
---
display_name: ""
week_repo_root: ""
pages_repo: ""
pages_url_base: ""
card_format: builtin
design_md: ""
accent: ""
downloads_dir: ""
python_cmd: ""
---
```

Below the front matter, write one line: "Personal settings for jungle-deck.
Gitignored. Field meanings: reference/local-template.md."

## Example (the author's values)

These are one student's values. They are an example only, not defaults.

```yaml
---
display_name: benjohnbill
week_repo_root: ~/dev/krafton-jungle
pages_repo: ~/dev/krafton-jungle/benjohnbill.github.io
pages_url_base: https://benjohnbill.github.io/
card_format: builtin
design_md: ~/dev/krafton-jungle/docs/slides/DESIGN.md
accent: ""
downloads_dir: /mnt/c/Users/benjohnbill/Downloads
python_cmd: python3
---
```
