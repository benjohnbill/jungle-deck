#!/usr/bin/env python3
"""Measure one jungle-deck run from its Claude Code transcript.

Development tool, not part of the skill. Reads <session>.jsonl and the
subagent transcripts in <session>/subagents/, then prints token use and the
checks of SPEC D7, D8, D9, D27 (ADR 0001).

Usage: python3 tools/measure_run.py <session.jsonl> [--json]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

PHASES = ("grill", "design", "build", "revise", "publish")
USAGE_KEYS = ("input_tokens", "output_tokens",
              "cache_creation_input_tokens", "cache_read_input_tokens")
SESSION_BREAK = "새 세션에서 'jungle-deck 이어서'"
SCREENSHOT_TOOL = re.compile(r"--screenshot|screenshot|cdp\.m?js|puppeteer|playwright", re.I)
CONTEXT_BASH = re.compile(r"\bgit (-C \S+ )?(log|show|diff|blame)\b|\bgh (issue|pr|api|project|repo)\b|curl .*github|\bcat |\bsed -n|\brg |\bgrep ")


def rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def usage(records):
    """Sum usage once per assistant message id; return (Counter, turns)."""
    total, seen = Counter(), set()
    for r in records:
        m = r.get("message") or {}
        if r.get("type") != "assistant" or m.get("id") in seen:
            continue
        seen.add(m.get("id"))
        for k in USAGE_KEYS:
            total[k] += (m.get("usage") or {}).get(k) or 0
    return total, len(seen)


def is_context_read(name, inp, blob):
    """A read of the student's material, not of the skill, BRIEF.md, or local.md."""
    if name in ("Agent", "Task", "WebFetch", "WebSearch") or name.startswith("mcp__plugin_claude-mem"):
        return True
    if "jungle-deck" in blob and not re.search(r"\bgit\b|\bgh\b", blob):
        return False
    if name in ("Read", "Grep", "Glob"):
        return "BRIEF.md" not in blob
    return name == "Bash" and bool(CONTEXT_BASH.search(inp.get("command", "")))


def is_skill_start(text):
    return "command-name>/jungle-deck" in text or (
        "Base directory for this skill" in text and "jungle-deck" in text)


def user_texts(m):
    c = m.get("content")
    if isinstance(c, str):
        return [c]
    return [b.get("text", "") for b in c or []
            if isinstance(b, dict) and b.get("type") == "text"]


def is_student_answer(text):
    t = text.strip()
    return bool(t) and not t.startswith("<") and "Base directory" not in t


def analyze(path):
    records = rows(path)
    main, turns = usage(records)
    subs = []
    sub_dir = Path(path).with_suffix("") / "subagents"
    for p in sorted(sub_dir.glob("*.jsonl")) if sub_dir.is_dir() else []:
        u, t = usage(rows(p))
        subs.append({"file": p.name, "turns": t, **u})

    phase, started, answered = None, False, False
    by_phase, seen = Counter(), set()
    reads_before_answer, agents_in_grill = [], []
    layout_runs, screenshot_calls, session_break = 0, [], 0
    for r in records:
        m = r.get("message") or {}
        if r.get("type") == "user":
            for t in user_texts(m):
                if not started and is_skill_start(t):
                    started = True
                elif started and not answered and is_student_answer(t):
                    answered = True
            continue
        if r.get("type") != "assistant":
            continue
        if m.get("id") not in seen and started:
            seen.add(m.get("id"))
            by_phase[phase or "setup"] += (m.get("usage") or {}).get("cache_read_input_tokens") or 0
        for b in m.get("content") or []:
            if b.get("type") == "text" and SESSION_BREAK in b.get("text", ""):
                session_break += 1
            if b.get("type") != "tool_use" or not started:
                continue
            name, blob = b["name"], json.dumps(b.get("input", {}), ensure_ascii=False)
            hits = re.findall(r"jungle-deck/reference/(%s)\.md" % "|".join(PHASES), blob)
            if hits and name in ("Read", "Bash"):
                phase = hits[-1]
            if not answered and is_context_read(name, b.get("input", {}), blob):
                reads_before_answer.append(f"{name} {blob[:90]}")
            if phase == "grill" and name in ("Agent", "Task"):
                agents_in_grill.append(b.get("input", {}).get("description", ""))
            if "check_layout.py" in blob:
                layout_runs += 1
            elif SCREENSHOT_TOOL.search(blob):
                screenshot_calls.append(f"{name} {blob[:90]}")

    return {
        "main": {"turns": turns, **main},
        "subagents": subs,
        "cache_read_by_phase": dict(by_phase),
        "checks": {
            "context_reads_before_first_answer": reads_before_answer,
            "subagents_in_grill": agents_in_grill,
            "check_layout_runs": layout_runs,
            "screenshot_tool_calls": screenshot_calls,
            "session_break_lines": session_break,
        },
    }


def show(res):
    m = res["main"]
    sub_read = sum(s["cache_read_input_tokens"] for s in res["subagents"])
    print(f"main: {m['turns']} turns, cache read {m['cache_read_input_tokens']:,}, "
          f"cache write {m['cache_creation_input_tokens']:,}, output {m['output_tokens']:,}")
    print(f"subagents: {len(res['subagents'])}, cache read {sub_read:,}")
    print("cache read by phase:", ", ".join(f"{k} {v:,}" for k, v in res["cache_read_by_phase"].items()))
    for k, v in res["checks"].items():
        print(f"{k}: {v if isinstance(v, int) else len(v)}")
        for line in v if isinstance(v, list) else []:
            print(f"  {line}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transcript")
    ap.add_argument("--json", action="store_true", help="print the record as JSON")
    a = ap.parse_args(argv)
    res = analyze(a.transcript)
    if a.json:
        json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        show(res)


if __name__ == "__main__":
    main()
