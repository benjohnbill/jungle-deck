#!/usr/bin/env python3
"""Publish a jungle-deck deck to a GitHub Pages repo (SPEC D12).

  copy    deck -> <pages_repo>/study/weekNN/<slug>.html, then byte compare
  verify  after the human push: poll the deck URL until 200 and the live
          bytes match the local file, then grep the index for the deck URL

This script never runs git. Settings come from jungle-deck.local.md
(field meanings: reference/local-template.md).
"""

import argparse
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
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
    pages = expand(settings["pages_repo"])
    if not pages.is_dir():
        raise Fail(f"pages_repo is not a directory: {pages}")
    dest = pages / "study" / week_dir(args.week) / f"{args.slug}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(deck, dest)
    if dest.read_bytes() != deck.read_bytes():
        raise Fail(f"copy differs from source: {dest} != {deck}")
    print(f"copied {deck} -> {dest}")
    return 0


def fetch(url):
    """GET url; return (status, body). status is None when unreachable."""
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        e.close()
        return e.code, b""
    except (urllib.error.URLError, OSError):
        return None, b""


def url_base(settings):
    """pages_url_base, or https://<owner>.github.io/ from the Pages repo's origin."""
    base = settings.get("pages_url_base", "")
    if not base:
        config = expand(settings["pages_repo"]) / ".git" / "config"
        text = config.read_text(encoding="utf-8") if config.is_file() else ""
        section = re.search(r'^\[remote "origin"\](.*?)(?=^\[|\Z)', text, re.M | re.S)
        url = re.search(r"^\s*url\s*=\s*(\S+)", section.group(1), re.M) if section else None
        owner = re.search(r"github\.com[:/]([^/]+)/", url.group(1)) if url else None
        if not owner:
            raise Fail(f"cannot derive the Pages URL from {config}: set pages_url_base")
        base = f"https://{owner.group(1).lower()}.github.io/"
    return base if base.endswith("/") else base + "/"


def live_state(deck_url, index_url, local_bytes):
    """Return None when the live site is right, else the reason it is not."""
    bust = f"?v={time.time_ns()}"  # skip the Pages CDN cache (max-age 600)
    status, body = fetch(deck_url + bust)
    if status != 200:
        return f"{deck_url} returned {status or 'no response'}"
    if body != local_bytes:
        return f"live deck differs from the local file: {deck_url}"
    status, index = fetch(index_url + bust)
    if status != 200:
        return f"index {index_url} returned {status or 'no response'}"
    if deck_url.encode() not in index:
        return f"index {index_url} has no card linking {deck_url}"
    return None


def cmd_verify(args, settings):
    deck = expand(args.deck)
    if not deck.is_file():
        raise Fail(f"deck not found: {deck}")
    local_bytes = deck.read_bytes()
    base = url_base(settings)
    deck_url = f"{base}study/{week_dir(args.week)}/{args.slug}.html"
    start = time.monotonic()
    while True:
        reason = live_state(deck_url, base, local_bytes)
        elapsed = time.monotonic() - start
        if reason is None:
            print(f"live, matching, and carded after {elapsed:.1f} s: {deck_url}")
            return 0
        if elapsed >= args.timeout:
            raise Fail(f"timeout after {elapsed:.1f} s: {reason}")
        time.sleep(min(args.interval, args.timeout - elapsed))


def parse_args(argv):
    p = argparse.ArgumentParser(prog="publish.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("copy", "verify"):
        s = sub.add_parser(name)
        s.add_argument("--deck", required=True, help="the source deck HTML")
        s.add_argument("--week", required=True, type=int, help="week number, e.g. 6 or 06")
        s.add_argument("--slug", help="deck slug (default: deck file name without .html)")
        s.add_argument("--local", default=str(SKILL_ROOT / "jungle-deck.local.md"),
                       help="settings file (default: jungle-deck.local.md in the skill root)")
        if name == "verify":
            s.add_argument("--timeout", type=float, default=600,
                           help="seconds to wait for the live deck (default: %(default)g)")
            s.add_argument("--interval", type=float, default=10,
                           help="seconds between polls (default: %(default)g)")
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
    return {"copy": cmd_copy, "verify": cmd_verify}[args.command](args, settings)


if __name__ == "__main__":
    sys.exit(main())
