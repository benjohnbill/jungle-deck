#!/usr/bin/env python3
"""Check the published cases (SPEC D28): files, tokens, figure parts, index, and names.

Run: python3 tools/check_cases.py [cases/<case> ...]
With no argument it checks every case and cases/INDEX.md.
Exit 0: no problem. Exit 1: one problem per line.

NAME_HASHES holds salted hashes, so the check runs in CI and the names of the
people it protects do not ship. A hit reports the file and line, not the name.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
INDEX = CASES / "INDEX.md"

SALT = "jungle-deck-cases:"
NAME_HASHES = frozenset({
    "01bd4010f06af2f7",
    "0791bf3fc5313669",
    "0c6496b9a72db62b",
    "0d601f6648938155",
    "173c69baf54a0fe8",
    "22ce885a3579e481",
    "2c3b5b1dee587290",
    "4115b0f7707af6bc",
    "49dfd13e7c754349",
    "4a0e046ec719ecb6",
    "597f0ca8b25643d5",
    "68afd9cfdbaf6c6f",
    "6ce7e455c055214d",
    "6da96b16459f2b50",
    "6f1cf93390077b55",
    "74eb3940882d9c4f",
    "7679a914026c7deb",
    "76fc96e299903a22",
    "8121e1578af9a7fe",
    "a6e7a438b646a885",
    "b5fc7dc0977cf2a8",
    "ce03bf6507a1d7b6",
    "d469c047720dcc39",
    "d65647c3adfce78a",
    "e6c7afb6aa2d08ef",
    "eec45dbfbae34418",
    "f015b3286fc4792f",
    "ffc65e2b41b69b72",
})
HANGUL_NAME_LENGTHS = (2, 3)

REQUIRED_COLORS = ("canvas", "ink", "primary", "ink-mute", "surface", "hairline")
REQUIRED_HEADINGS = ("## The one rule", "## Slides", "## CSS to add", "## Figure vocabulary", "## Do not")
MIN_SVG_FONT = 12
MAX_PREVIEW_BYTES = 300_000
TEXT_FILES = ("DESIGN.md", "BRIEF.md")

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.S)
RAW_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")
ID = re.compile(r"\bid=\"([^\"]+)\"")
SVG_FONT = re.compile(r"font-size=\"([\d.]+)\"")
STACKED_SVG = re.compile(r"<svg[^>]*\bclass=\"[^\"]*\bfr\b")
PART = re.compile(r"^\*\*([^*]+?)\.\*\*", re.M)
INDEX_ROW = re.compile(r"^\| \[([^\]]+)\]\(([^)]+)\) \|(.*) \|$", re.M)
LINK = re.compile(r"\]\(([^)#\s]+)")


def digest(text):
    return hashlib.sha256((SALT + text).encode()).hexdigest()[:16]


def name_hits(text, hashes=NAME_HASHES):
    """1-based line numbers that hold a protected name.

    Latin: a whole token, or a hyphen-separated part of one, ignoring case.
    Hangul: any run of 2 or 3 syllables, because particles attach to names.
    """
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        tokens = re.findall(r"[A-Za-z0-9_-]+", line.lower())
        latin = set(tokens) | {p for t in tokens for p in re.split(r"[-_]", t)}
        hangul = {run[i:i + k] for run in re.findall(r"[\uac00-\ud7a3]+", line)
                  for k in HANGUL_NAME_LENGTHS for i in range(len(run) - k + 1)}
        if any(digest(w) in hashes for w in latin | hangul):
            hits.append(n)
    return hits


def color_keys(front):
    block = re.search(r"^colors:\n((?:[ \t]+.*\n?)+)", front, re.M)
    return re.findall(r"^\s+([\w-]+):", block.group(1), re.M) if block else []


def check_design(path):
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        return [f"{path}: no front matter"]
    front = match.group(1)
    problems = [f"{path}: front matter has no {key}:" for key in ("name", "description", "typography")
                if not re.search(rf"^{key}:", front, re.M)]
    keys = color_keys(front)
    problems += [f"{path}: colors has no {key}" for key in REQUIRED_COLORS if key not in keys]
    problems += [f"{path}: missing heading {h!r}" for h in REQUIRED_HEADINGS
                 if not re.search(rf"^{re.escape(h)}\s*$", text, re.M)]
    if not PART.search(text):
        problems.append(f"{path}: no figure part (a line that starts with **Name.**)")
    for block in FENCE.findall(text[match.end():]):
        for pattern, why in ((RAW_COLOR, "a raw color in a snippet: use var(--...)"),
                             (STACKED_SVG, "stacked <svg class=fr>: use one <svg> with <g class=fr>")):
            if pattern.search(block):
                problems.append(f"{path}: {why}: {pattern.search(block).group(0)}")
        problems += [f"{path}: id {i!r} has no SLOT prefix" for i in ID.findall(block)
                     if not i.startswith("SLOT")]
        problems += [f"{path}: font-size {s} is under {MIN_SVG_FONT}" for s in SVG_FONT.findall(block)
                     if float(s) < MIN_SVG_FONT]
    return problems


def check_brief(path):
    text = path.read_text(encoding="utf-8")
    problems = []
    if re.search(r"^phase:", text, re.M):
        problems.append(f"{path}: has phase:, so it reads as a live BRIEF")
    if not re.search(r"^kind: case-record$", text, re.M):
        problems.append(f"{path}: front matter needs kind: case-record")
    return problems


def check_case(folder):
    folder = Path(folder)
    design = folder / "DESIGN.md"
    if not design.is_file():
        return [f"{folder}: no DESIGN.md"]
    problems = check_design(design)
    if (folder / "BRIEF.md").is_file():
        problems += check_brief(folder / "BRIEF.md")
    preview = folder / "preview.png"
    if not preview.is_file():
        problems.append(f"{folder}: no preview.png")
    elif preview.stat().st_size > MAX_PREVIEW_BYTES:
        problems.append(f"{folder}: preview.png is over {MAX_PREVIEW_BYTES} bytes")
    for name in TEXT_FILES:
        path = folder / name
        if path.is_file():
            problems += [f"{path}:{n}: a protected name" for n in name_hits(path.read_text(encoding="utf-8"))]
    return problems


def check_index():
    if not INDEX.is_file():
        return [f"{INDEX}: missing"]
    text = INDEX.read_text(encoding="utf-8")
    problems = [f"{INDEX}:{n}: a protected name" for n in name_hits(text)]
    problems += [f"{INDEX}: broken link {link}" for link in LINK.findall(text)
                 if "://" not in link and not (CASES / link).exists()]
    rows = {}
    for label, link, rest in INDEX_ROW.findall(text):
        rows[label] = rest
        if link != f"{label}/DESIGN.md":
            problems.append(f"{INDEX}: row {label} links to {link}")
    folders = {p.name for p in CASES.iterdir() if p.is_dir()}
    problems += [f"{INDEX}: no row for {f}" for f in sorted(folders - set(rows))]
    problems += [f"{INDEX}: row {r} has no folder" for r in sorted(set(rows) - folders)]
    for label in sorted(set(rows) & folders):
        design = CASES / label / "DESIGN.md"
        if not design.is_file():
            continue
        parts = set(PART.findall(design.read_text(encoding="utf-8")))
        listed = re.findall(r"`([^`]+)`", rows[label].rsplit("|", 1)[-1])
        if not listed:
            problems.append(f"{INDEX}: row {label} lists no figure part")
        problems += [f"{INDEX}: row {label} lists {p!r}, not a part of its DESIGN.md"
                     for p in listed if p not in parts]
    return problems


def check_all():
    problems = check_index()
    for folder in sorted(p for p in CASES.iterdir() if p.is_dir()):
        problems += check_case(folder)
    return problems


def main(argv):
    problems = [p for a in argv for p in check_case(a)] if argv else check_all()
    for problem in problems:
        print(problem)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
