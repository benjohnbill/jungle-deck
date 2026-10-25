#!/usr/bin/env python3
"""Drive one revision of jungle-deck in headless Claude Code sessions.

Development tool for the verify-jungle-deck skill. A run directory holds:
  plugin/   the skill at <rev>, loaded with --plugin-dir as `jdv:jungle-deck`
  jungle-deck.local.md  the run's settings, passed as JUNGLE_DECK_CONFIG (the user's
            settings are never read). A copy also sits in the skill folder, where a
            revision before 2026-10-26 reads it
  week09/   a synthetic student repo with commits in the last 7 days
  state.json  the revision, the sessions, and every turn

Usage:
  jdv.py stage <run-dir> <rev>          make the plugin and the fixture repo
  jdv.py turn <run-dir> <message> [--new]   one student turn; --new starts a session
  jdv.py report <run-dir> [<run-dir>...]    token use, rule checks, artifacts
  jdv.py clean <run-dir>                stop processes the run started; keep evidence
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tarfile
import io
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import measure_run  # noqa: E402

PLUGIN = "jdv"
STUDENT = ("홍길동", "student@example.com")
TEAMMATE = ("김팀원", "teammate@example.com")
TOOLS = "Bash Read Write Edit Glob Grep Skill"
LOCAL_MD = """---
display_name: "홍길동"
notes_url: ""
design_md: ""
accent: ""
downloads_dir: ""
python_cmd: "python3"
current_brief: ""
prev_brief: ""
pages_repo: ""
pages_dir: ""
pages_url_base: ""
card_format: builtin
---
Personal settings for jungle-deck.
Gitignored. Field meanings: reference/local-template.md.
"""

# (author, days ago, message, {path: content})
HISTORY = [
    (STUDENT, 6, "vm: grow the stack on a page fault", {
        "vm/stack.c": "bool vm_try_grow (void *addr, void *esp) {\n"
                      "  /* PUSHA writes 32 bytes below esp */\n"
                      "  if (addr < esp - 32) return false;\n"
                      "  return vm_alloc_stack_page (pg_round_down (addr));\n}\n",
        "run_tests.py": "import pathlib\n"
                        "src = pathlib.Path('vm/stack.c').read_text()\n"
                        "ok = 'f->rsp' in src\n"
                        "for t in ['pt-grow-stack', 'pt-grow-pusha', 'pt-big-stk-obj']:\n"
                        "    print(('pass' if ok or t == 'pt-grow-pusha' else 'FAIL') + ' tests/vm/' + t)\n"
                        "print('All 3 tests passed.' if ok else '2 of 3 tests failed.')\n",
    }),
    (TEAMMATE, 5, "docs: team convention for branch names", {
        "CONVENTION.md": "# Convention\n\nBranch: feat/<area>-<topic>\n"}),
    (STUDENT, 4, "test: stack growth fails in syscalls", {
        "notes/2026-week09.md": "# week09\n\n- pt-grow-stack fails only when the fault comes from a syscall.\n"
                                "- In a syscall, the intr_frame rsp is the kernel stack, not the user stack.\n"}),
    (STUDENT, 2, "fix: save the user rsp on syscall entry and use it in the fault handler", {
        "vm/stack.c": "bool vm_try_grow (void *addr, struct intr_frame *f) {\n"
                      "  void *rsp = f->rsp_user_saved ? thread_current ()->user_rsp : f->rsp;\n"
                      "  if (addr < rsp - 8) return false;\n"
                      "  return vm_alloc_stack_page (pg_round_down (addr));\n}\n"}),
]


def run(argv, **kw):
    return subprocess.run(argv, check=True, stdout=subprocess.PIPE, encoding="utf-8", **kw).stdout


def load(run_dir):
    return json.loads((Path(run_dir) / "state.json").read_text(encoding="utf-8"))


def save(run_dir, state):
    (Path(run_dir) / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def stage(run_dir, rev):
    run_dir = Path(run_dir).resolve()
    if (run_dir / "state.json").exists():
        sys.exit("%s is already staged" % run_dir)
    skill = run_dir / "plugin" / "skills" / "jungle-deck"
    skill.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(REPO), "archive", rev], check=True, stdout=subprocess.PIPE).stdout
    tarfile.open(fileobj=io.BytesIO(archive)).extractall(skill)
    for settings in (run_dir / "jungle-deck.local.md", skill / "jungle-deck.local.md"):
        settings.write_text(LOCAL_MD, encoding="utf-8")
    meta = run_dir / "plugin" / ".claude-plugin"
    meta.mkdir()
    (meta / "plugin.json").write_text(json.dumps(
        {"name": PLUGIN, "version": "0.0.0", "description": "jungle-deck at " + rev}), encoding="utf-8")

    repo = run_dir / "week09"
    repo.mkdir()
    run(["git", "init", "-q", "-b", "main", str(repo)])
    run(["git", "-C", str(repo), "config", "user.name", STUDENT[0]])
    run(["git", "-C", str(repo), "config", "user.email", STUDENT[1]])
    for (name, email), days, message, files in HISTORY:
        for path, text in files.items():
            (repo / path).parent.mkdir(parents=True, exist_ok=True)
            (repo / path).write_text(text, encoding="utf-8")
        run(["git", "-C", str(repo), "add", "-A"])
        when = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        env = dict(os.environ, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_AUTHOR_DATE=when,
                   GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email, GIT_COMMITTER_DATE=when)
        run(["git", "-C", str(repo), "commit", "-q", "-m", message], env=env)
    save(run_dir, {"rev": run(["git", "-C", str(REPO), "rev-parse", "--short", rev]).strip(),
                   "plugin": str(run_dir / "plugin"), "repo": str(repo), "sessions": [], "turns": []})
    print("staged %s at %s: plugin %s, repo %s" % (run_dir, rev, run_dir / "plugin", repo))


def transcript_of(repo, session):
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(repo))
    return str(Path.home() / ".claude" / "projects" / slug / (session + ".jsonl"))


def turn(run_dir, message, new):
    state = load(run_dir)
    argv = ["claude", "-p", message, "--plugin-dir", state["plugin"], "--output-format", "json",
            "--permission-mode", "acceptEdits", "--allowedTools", TOOLS]
    if state["sessions"] and not new:
        argv += ["--resume", state["sessions"][-1]]
    env = dict(os.environ, JUNGLE_DECK_CONFIG=str(Path(run_dir).resolve() / "jungle-deck.local.md"))
    p = subprocess.run(argv, cwd=state["repo"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       encoding="utf-8", errors="replace", timeout=1800)
    try:
        out = json.loads(p.stdout)
    except ValueError:
        sys.exit("claude -p failed (%d): %s" % (p.returncode, (p.stderr or p.stdout)[-2000:]))
    sid = out["session_id"]
    if not state["sessions"] or new or state["sessions"][-1] != sid:
        state["sessions"].append(sid)
    state["turns"].append({"session": sid, "message": message, "result": out.get("result", ""),
                           "cost_usd": out.get("total_cost_usd")})
    save(run_dir, state)
    print("[session %s, turn %d]" % (sid, len(state["turns"])))
    print(out.get("result", ""))


def brief_of(repo):
    found = sorted(Path(repo).glob("**/BRIEF.md"))
    return found[0] if found else None


def report(run_dirs):
    for run_dir in run_dirs:
        state = load(run_dir)
        total = {"turns": 0, "cache_read": 0, "output": 0, "subagent_cache_read": 0}
        checks = {}
        for sid in state["sessions"]:
            res = measure_run.analyze(transcript_of(state["repo"], sid))
            total["turns"] += res["main"]["turns"]
            total["cache_read"] += res["main"]["cache_read_input_tokens"]
            total["output"] += res["main"]["output_tokens"]
            total["subagent_cache_read"] += sum(s["cache_read_input_tokens"] for s in res["subagents"])
            for k, v in res["checks"].items():
                n = v if isinstance(v, int) else len(v)
                checks[k] = checks.get(k, 0) + n
        cost = sum(t["cost_usd"] or 0 for t in state["turns"])
        brief = brief_of(state["repo"])
        phase = re.search(r"(?m)^phase:\s*(\S+)", brief.read_text(encoding="utf-8")).group(1) if brief else None
        pages = sorted(str(p) for p in Path(state["repo"]).glob("**/*.html") if "previews" not in p.parts)
        print("== %s (rev %s): %d sessions, %d student turns, $%.2f"
              % (run_dir, state["rev"], len(state["sessions"]), len(state["turns"]), cost))
        print("   tokens: " + ", ".join("%s %s" % (k, format(v, ",")) for k, v in total.items()))
        print("   checks: " + ", ".join("%s %d" % kv for kv in checks.items()))
        print("   brief: %s (phase %s)" % (brief, phase))
        print("   pages: %s" % (", ".join(pages) or "none"))


def clean(run_dir):
    run_dir = str(Path(run_dir).resolve())
    out = subprocess.run(["pgrep", "-f", run_dir], stdout=subprocess.PIPE, encoding="utf-8").stdout.split()
    mine = [pid for pid in out if int(pid) != os.getpid()]
    for pid in mine:
        subprocess.run(["kill", pid])
    print("stopped %d process(es) started under %s; evidence kept" % (len(mine), run_dir))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage"); s.add_argument("run_dir"); s.add_argument("rev")
    t = sub.add_parser("turn"); t.add_argument("run_dir"); t.add_argument("message"); t.add_argument("--new", action="store_true")
    r = sub.add_parser("report"); r.add_argument("run_dirs", nargs="+")
    c = sub.add_parser("clean"); c.add_argument("run_dir")
    a = ap.parse_args()
    if a.cmd == "stage":
        stage(a.run_dir, a.rev)
    elif a.cmd == "turn":
        turn(a.run_dir, a.message, a.new)
    elif a.cmd == "report":
        report(a.run_dirs)
    else:
        clean(a.run_dir)


if __name__ == "__main__":
    main()
