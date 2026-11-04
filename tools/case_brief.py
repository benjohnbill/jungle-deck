#!/usr/bin/env python3
"""Write the public record of a finished talk from its BRIEF.md (SPEC D28).

Run: python3 tools/case_brief.py <BRIEF.md> <cases/<case>/BRIEF.md> --map <local.json>

The map stays out of the repo, because it holds real names:
  {"replace": [["regex", "text"], ...], "drop": ["heading text", ...]}
Replacements run in order. A dropped heading goes with everything under it,
up to the next heading of the same or a higher level.
Rerun is safe: the output is a pure function of the input and the map.
Then run tools/check_cases.py, which scans the output for protected names.
"""
import argparse
import json
import re
from pathlib import Path

ALWAYS_DROP = ("Next action", "Context notes", "Build", "Publish")
TEMPLATE_LINE = re.compile(r"^(D7 \(|Filled in `|What `|One line per round)")
PRONOUNS = (("He", "The student"), ("he", "the student"), ("His", "The student's"),
            ("his", "the student's"), ("him", "the student"), ("himself", "on their own"))


def drop_sections(text, headings):
    out, skip_level = [], None
    for line in text.splitlines():
        match = re.match(r"(#+) (.*)", line)
        if match:
            level = len(match.group(1))
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and match.group(2).strip() in headings:
                skip_level = level
        if skip_level is None:
            out.append(line)
    return "\n".join(out)


def public_record(text, case, rules):
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    body = drop_sections(body, set(ALWAYS_DROP) | set(rules.get("drop", ())))
    body = "\n".join(line for line in body.splitlines() if not TEMPLATE_LINE.match(line))
    for pattern, repl in rules.get("replace", ()):
        body = re.sub(pattern, repl, body)
    for word, repl in PRONOUNS:
        body = re.sub(rf"\b{word}\b", repl, body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    head = (f"---\nkind: case-record\ncase: {case}\n"
            "status: A finished talk. A record of how it was planned, not rules to follow\n---\n\n")
    return head + body + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--map", type=Path, required=True)
    args = parser.parse_args()
    rules = json.loads(args.map.read_text(encoding="utf-8"))
    record = public_record(args.source.read_text(encoding="utf-8"), args.output.parent.name, rules)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(record, encoding="utf-8")


if __name__ == "__main__":
    main()
