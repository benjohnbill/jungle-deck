# jungle-deck

A Claude Code skill that builds a 2-minute Krafton Jungle presentation deck
as one HTML file. It runs in four phases: `grill → build → revise → publish`.
It keeps its state in a `BRIEF.md` beside the deck, so you can stop and
resume at any time. The design is in [SPEC.md](SPEC.md).

## Install

```bash
git clone https://github.com/benjohnbill/jungle-deck ~/.claude/skills/jungle-deck
```

The skill works best with the
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) skill
installed. Without it, jungle-deck uses the copies in `vendor/frontend-slides/`.

## First run

1. Open Claude Code in your week repository.
2. Say "발표 덱" or type `/jungle-deck`.
3. Answer a few setup questions (display name, week-repo root, publish
   target). The skill writes the answers to `jungle-deck.local.md` in the
   skill directory. This file is gitignored.
4. The `grill` phase starts. It asks you to settle the conclusion, the story,
   and one thesis sentence per slide before any slide is built.

## Credits

Slide styles, the viewport base CSS, and the HTML template come from
[frontend-slides](https://github.com/zarazhangrui/frontend-slides) by Zara
Zhang, under the MIT License. See `vendor/frontend-slides/SOURCE.md` for the
exact upstream commit.

## License

MIT. See [LICENSE](LICENSE).
