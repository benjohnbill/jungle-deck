# jungle-deck

A Claude Code skill that builds a 2-minute Krafton Jungle presentation deck
as one HTML file. It runs in four phases: `grill → build → revise → publish`.
It keeps its state in a `BRIEF.md` beside the deck, so you can stop and
resume at any time. The design is in [SPEC.md](SPEC.md).

## Requirements

- Claude Code on macOS, Windows, Linux, or WSL.
- Python 3.8 or later. The first run finds a working command (`python3`,
  `python`, or `py -3`). If none works, it tells you how to install
  Python for your OS and stops. It does not install anything.
- git.

## Install

macOS, Linux, WSL:

```bash
git clone https://github.com/benjohnbill/jungle-deck ~/.claude/skills/jungle-deck
```

Windows (PowerShell):

```powershell
git clone https://github.com/benjohnbill/jungle-deck "$HOME\.claude\skills\jungle-deck"
```

The skill works best with the
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) skill
installed. Without it, jungle-deck uses the copies in `vendor/frontend-slides/`.

## First run

1. Open Claude Code in your week repository.
2. Say "발표 덱" or type `/jungle-deck`.
3. The skill checks Python first. Then answer six setup questions:
   display name, week-repo root, GitHub Pages repo, DESIGN.md, accent,
   and downloads folder. The downloads default is detected for your OS.
   Answer "기본값" to take every default. The skill writes the answers and
   the Python command to `jungle-deck.local.md` in the skill directory.
   This file is gitignored. Without a Pages repo, the skill stops at a
   finished local HTML file.
4. The skill makes a new deck folder with a `BRIEF.md`, and the `grill`
   phase starts. It asks you to settle the conclusion, the story, and one
   thesis sentence per slide before any slide is built.

Later calls read `BRIEF.md` and resume at its phase. Say
"jungle-deck 이어서" to continue a deck, or "덱 게시" to publish it.

## Credits

Slide styles, the viewport base CSS, and the HTML template come from
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) by Zara
Zhang, under the MIT License. See `vendor/frontend-slides/SOURCE.md` for the
exact upstream commit.

## License

MIT. See [LICENSE](LICENSE).
