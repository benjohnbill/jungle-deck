#!/usr/bin/env python3
"""Merge a browser export of a deck back into its source (SPEC D11).

The deck's Ctrl+S saves a copy into the downloads folder, not over the
source. That copy is the browser's serialization of the live DOM, so it
must not replace the source wholesale. Only the inside of each
<section class="slide" id="..."> is carried over, matched by id; speaker
notes ride along because <aside class="notes"> sits inside its section.

Dry-run by default: print a unified diff per changed section and a
summary line. --write needs the --export that the dry-run read. It copies
the deck to _backup/ next to it, then atomically replaces only the changed
sections and leaves every byte outside them (head, styles, scripts) as it was.
"""

import argparse
import difflib
import os
import re
import shlex
import shutil
import sys
import tempfile
import time
from pathlib import Path

# Comments are matched first so a <section> written inside one (the
# template's header documents the format that way) is skipped.
SECTION = re.compile(r"<!--.*?-->|(<section\b[^>]*>)(.*?)(</section>)", re.S)
ATTR_ID = re.compile(r'\bid="([^"]+)"')
ATTR_CLASS = re.compile(r'\bclass="([^"]*)"')


def sections(html):
    """Yield (id, match) for every slide section, in document order."""
    for m in SECTION.finditer(html):
        if m.group(1) is None:
            continue
        cls = ATTR_CLASS.search(m.group(1))
        sid = ATTR_ID.search(m.group(1))
        if cls and "slide" in cls.group(1).split() and sid:
            yield sid.group(1), m


def clean(inner):
    """Undo what the live page and the editor leave in a section: edit
    attributes, typed non-breaking spaces, and the slide number the
    runtime writes into .head .num."""
    inner = re.sub(r'\s+contenteditable="[^"]*"', "", inner)
    inner = inner.replace("&nbsp;", " ").replace("\u00a0", " ")
    inner = re.sub(r'(<span class="num">)[^<]*(</span>)', r"\1\2", inner)
    return inner


def lf(text):
    """CRLF to LF: the one newline rule for comparing and for diffs."""
    return text.replace("\r\n", "\n")


def same(a, b):
    """Equal up to serialization: browsers write a text '>' as '&gt;', and
    the HTML parser turns CRLF into LF."""
    norm = lambda t: lf(t).replace("&gt;", ">")
    return norm(a) == norm(b)


WIN_USERS = Path("/mnt/c/Users")


def default_downloads():
    """The Windows downloads folder seen from WSL, else ~/Downloads. On WSL
    the Windows user name can differ from $USER: say so, do not guess further."""
    user = os.environ.get("USER", "")
    win = WIN_USERS / user / "Downloads"
    if user and win.is_dir():
        return win
    if WIN_USERS.is_dir():
        print(f"pull_edits: {win} not found; using ~/Downloads. "
              "Pass --downloads <Windows downloads folder> if the export is there.",
              file=sys.stderr)
    return Path.home() / "Downloads"


def find_export(deck, downloads):
    """The newest browser copy of deck in downloads: the same file name, or
    with the counter browsers add on a clash ('deck (1).html', 'deck(1).html').
    A bare prefix is not enough: 'deck-v2.html' is another deck."""
    name = re.compile(re.escape(deck.stem) + r"(?: ?\(\d+\))?\.html")
    copies = [p for p in downloads.glob("*.html") if name.fullmatch(p.name)]
    if not copies:
        raise Fail(f"no {deck.stem}*.html export in {downloads}")
    return max(copies, key=lambda p: p.stat().st_mtime)


class Fail(Exception):
    """A one-line reason to exit non-zero."""


def read_keeping_newlines(path):
    # newline="" keeps CRLF and the like, so --write changes only the sections.
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def backup(deck):
    """Copy deck to <deck dir>/_backup/<stem>.<YYYYmmdd-HHMMSS>.html; return the path."""
    folder = deck.parent / "_backup"
    folder.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest, n = folder / f"{deck.stem}.{stamp}.html", 1
    while dest.exists():  # two writes in one second: keep both backups
        dest, n = folder / f"{deck.stem}.{stamp}-{n}.html", n + 1
    shutil.copy2(deck, dest)
    return dest


def write_atomic(path, text):
    """Write text to a temp file next to path, then rename it over path."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def merge(deck, export, write):
    src = read_keeping_newlines(deck)
    src_sections = list(sections(src))
    new = {sid: clean(m.group(2)) for sid, m in sections(read_keeping_newlines(export))}
    src_ids = [sid for sid, _ in src_sections]
    if not set(src_ids) & set(new):
        raise Fail(f"{export}: no matching sections (deck ids: {', '.join(src_ids) or 'none'})")
    missing = [sid for sid in src_ids if sid not in new]
    extra = [sid for sid in new if sid not in src_ids]

    print(f"export: {export}")
    changed, unchanged, edits = [], [], []
    for sid, m in src_sections:
        if sid not in new:
            continue
        if same(clean(m.group(2)), new[sid]):
            unchanged.append(sid)
            continue
        changed.append(sid)
        inner = lf(new[sid])
        if "\r\n" in src:
            inner = inner.replace("\n", "\r\n")
        edits.append((m.start(2), m.end(2), inner))
        diff = difflib.unified_diff(
            m.group(2).splitlines(), new[sid].splitlines(),
            f"{deck.name}#{sid}", f"{export.name}#{sid}", lineterm="")
        print("\n".join(diff))

    summary = f"{len(changed)} changed, {len(unchanged)} unchanged"
    if missing:
        summary += f"; missing in export: {', '.join(missing)} (kept as is)"
    if extra:
        summary += f"; extra in export: {', '.join(extra)} (not added)"
    print(summary)

    if not write:
        if edits:
            print("dry-run: nothing written. To write this export, run:")
            print("  " + shlex.join(["python3", str(Path(__file__).resolve()),
                                     "--deck", str(deck.resolve()),
                                     "--export", str(export.resolve()), "--write"]))
        return
    if edits:
        out = src
        for start, end, inner in reversed(edits):
            out = out[:start] + inner + out[end:]
        print(f"backup: {backup(deck)}")
        write_atomic(deck, out)
        print(f"wrote {', '.join(changed)} into {deck}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deck", required=True, type=Path, help="the deck source HTML")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--export", type=Path, help="the exported copy to merge")
    src.add_argument("--downloads", type=Path,
                     help="where to look for the newest export (default: "
                          "/mnt/c/Users/$USER/Downloads if present, else ~/Downloads)")
    ap.add_argument("--write", action="store_true",
                    help="apply the changed sections to the deck (default: dry-run); "
                         "needs --export")
    args = ap.parse_args(argv)
    if args.write and not args.export:
        print("pull_edits: --write needs --export FILE (the export you reviewed in the dry-run)",
              file=sys.stderr)
        return 2
    try:
        export = args.export or find_export(args.deck, args.downloads or default_downloads())
        merge(args.deck, export, args.write)
    except (Fail, OSError) as e:
        print(f"pull_edits: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
