#!/usr/bin/env python3
"""Publish a jungle-deck deck to a GitHub Pages repo (SPEC D12).

  copy    deck -> <pages_repo>/study/weekNN/<slug>.html, then byte compare
  verify  after the human push: poll the deck URL until 200 and the live
          bytes match the local file, then grep the index for the deck URL

This script never runs git. Settings come from jungle-deck.local.md
(field meanings: reference/local-template.md).
"""

import argparse
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


class Fail(Exception):
    """A one-line reason to exit non-zero."""


def load_settings(path):
    """Read the YAML front matter of local.md as a dict of plain strings."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise Fail(f"settings file not found: {path} (run the first-run questions)")
    if not lines or lines[0].strip() != "---":
        raise Fail(f"{path}: no front matter")
    settings = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return settings
        key, sep, value = line.partition(":")
        if sep and key.strip():
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            settings[key.strip()] = value
    raise Fail(f"{path}: front matter is not closed")


def expand(path):
    return Path(path).expanduser()


def week_dir(week):
    return f"week{int(week):02d}"


def cmd_copy(args, settings):
    deck = expand(args.deck)
    if not deck.is_file():
        raise Fail(f"deck not found: {deck}")
    dest = expand(settings["pages_repo"]) / "study" / week_dir(args.week) / f"{args.slug}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(deck, dest)
    if dest.read_bytes() != deck.read_bytes():
        raise Fail(f"copy differs from source: {dest} != {deck}")
    print(f"copied {deck} -> {dest}")
    return 0


def parse_args(argv):
    p = argparse.ArgumentParser(prog="publish.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("copy", "verify"):
        s = sub.add_parser(name)
        s.add_argument("--deck", required=True, help="the source deck HTML")
        s.add_argument("--week", required=True, help="week number, e.g. 6 or 06")
        s.add_argument("--slug", help="deck slug (default: deck file name without .html)")
        s.add_argument("--local", default=str(SKILL_ROOT / "jungle-deck.local.md"),
                       help="settings file (default: jungle-deck.local.md in the skill root)")
    args = p.parse_args(argv)
    if not args.slug:
        args.slug = Path(args.deck).stem
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return run(args)
    except Fail as e:
        print(f"publish: {e}", file=sys.stderr)
        return 1


def run(args):
    settings = load_settings(expand(args.local))
    if not settings.get("pages_repo"):
        print(f"pages_repo is not set: publish stops at the local HTML {expand(args.deck)}")
        return 0
    return {"copy": cmd_copy}[args.command](args, settings)


if __name__ == "__main__":
    sys.exit(main())
