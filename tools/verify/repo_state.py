#!/usr/bin/env python3
"""Report whether this checkout is safe to hand over: read-only, one line per check.

Run: python3 tools/verify/repo_state.py [--full] [--repo <path>]
--full also runs the test suite in a fresh clone of HEAD, which shows the tests
do not depend on an untracked or ignored file.
Exit 0: every check passed. Exit 1: at least one FAIL. A SKIP is not a pass:
it means the check could not look (no gh, not logged in, no upstream).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_cases  # noqa: E402

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
TEST_TIMEOUT_S = 600


def sh(repo, *argv):
    return subprocess.run(argv, cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding="utf-8", errors="replace")


def git(repo, *argv):
    return sh(repo, "git", *argv)


def gh_json(repo, *argv):
    """The parsed output of a gh command, or None when gh cannot answer."""
    try:
        out = sh(repo, "gh", *argv)
    except OSError:
        return None
    return json.loads(out.stdout) if out.returncode == 0 else None


def working_tree(repo):
    out = git(repo, "status", "--porcelain").stdout.strip()
    return (PASS, "clean") if not out else (FAIL, "%d changed paths" % len(out.splitlines()))


def pushed(repo):
    upstream = git(repo, "rev-parse", "--abbrev-ref", "@{upstream}")
    if upstream.returncode != 0:
        return SKIP, "no upstream"
    ahead = git(repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}").stdout.split()
    detail = "%s ahead, %s behind %s" % (ahead[0], ahead[1], upstream.stdout.strip())
    return (PASS if ahead == ["0", "0"] else FAIL), detail


def cases_pass(repo):
    problems = check_cases.check_all()
    return (PASS, "ok") if not problems else (FAIL, problems[0])


def name_history(repo, hashes=check_cases.NAME_HASHES):
    """Protected names in any line ever added under cases/, on any ref."""
    log = git(repo, "log", "--all", "-p", "--format=", "--", "cases").stdout
    added = "\n".join(line[1:] for line in log.splitlines()
                      if line.startswith("+") and not line.startswith("+++"))
    hits = check_cases.name_hits(added, hashes)
    return (PASS, "no hit in history") if not hits else (FAIL, "%d added lines hold a name" % len(hits))


def ci_on_head(repo):
    sha = git(repo, "rev-parse", "HEAD").stdout.strip()
    runs = gh_json(repo, "run", "list", "--commit", sha, "--json", "status,conclusion,event")
    if runs is None:
        return SKIP, "gh gave no answer"
    if not runs:
        return FAIL, "no run for %s: pushed?" % sha[:7]
    if any(r["status"] != "completed" for r in runs):
        return FAIL, "still running on %s" % sha[:7]
    bad = [r["event"] for r in runs if r["conclusion"] != "success"]
    return (FAIL, "failed: %s" % ", ".join(bad)) if bad else (PASS, "%d runs on %s" % (len(runs), sha[:7]))


def ci_on_main(repo):
    runs = gh_json(repo, "run", "list", "--branch", "main", "--event", "push", "--limit", "1",
                   "--json", "conclusion,headSha")
    if not runs:
        return SKIP, "gh gave no answer"
    return (PASS if runs[0]["conclusion"] == "success" else FAIL), "%s on %s" % (
        runs[0]["conclusion"], runs[0]["headSha"][:7])


def open_pr(repo):
    pr = gh_json(repo, "pr", "view", "--json", "number,state,mergeable")
    if pr is None:
        return SKIP, "no PR for this branch"
    detail = "#%s %s %s" % (pr["number"], pr["state"], pr["mergeable"])
    return (FAIL if pr["mergeable"] == "CONFLICTING" else PASS), detail


def fresh_clone_tests(repo):
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "clone"
        git(repo, "clone", "-q", "--no-hardlinks", str(repo), str(clone))
        out = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=str(clone),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8",
                             errors="replace", timeout=TEST_TIMEOUT_S)
    last = out.stdout.strip().splitlines()[-1]
    return (PASS if out.returncode == 0 else FAIL), last


CHECKS = (("working tree", working_tree), ("pushed", pushed), ("cases", cases_pass),
          ("names in history", name_history), ("CI on HEAD", ci_on_head),
          ("CI on main", ci_on_main), ("pull request", open_pr))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--repo", type=Path, default=HERE.parent.parent)
    args = parser.parse_args()
    checks = CHECKS + ((("tests in a fresh clone", fresh_clone_tests),) if args.full else ())
    failed = False
    for name, check in checks:
        verdict, detail = check(args.repo)
        print("%s  %s: %s" % (verdict, name, detail))
        failed = failed or verdict == FAIL
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
