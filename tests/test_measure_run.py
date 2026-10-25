"""Checks for tools/measure_run.py (ADR 0001 verification oracle).

Run: python3 -m unittest discover -s tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import measure_run  # noqa: E402


def assistant(mid, *blocks, read=0):
    return {"type": "assistant", "message": {
        "id": mid, "usage": {"cache_read_input_tokens": read}, "content": list(blocks)}}


def tool(name, **inp):
    return {"type": "tool_use", "id": name + str(len(inp)), "name": name, "input": inp}


def user(text):
    return {"type": "user", "message": {"content": text}}


START = user("<command-name>/jungle-deck</command-name>")


class MeasureRunTest(unittest.TestCase):
    def run_on(self, records):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
            return measure_run.analyze(p)

    def test_a_git_log_before_the_first_answer_is_flagged(self):
        res = self.run_on([
            START,
            assistant("a", tool("Read", file_path="/s/jungle-deck/reference/grill.md"), read=10),
            assistant("b", tool("Bash", command="git -C /r log --stat"), read=20),
            user("커밋 보고 정할게요"),
        ])
        self.assertEqual(len(res["checks"]["context_reads_before_first_answer"]), 1)
        self.assertEqual(res["cache_read_by_phase"], {"setup": 10, "grill": 20})

    def test_skill_files_and_reads_after_the_answer_pass(self):
        res = self.run_on([
            START,
            assistant("a", tool("Read", file_path="/s/jungle-deck/reference/grill.md"),
                      {"type": "text", "text": "이번 주에 발표하고 싶은 아이템이나 ..."}),
            user("페이지 폴트 디버깅 얘기 할래요"),
            assistant("b", tool("Bash", command="git log --stat"),
                      tool("Agent", description="research")),
        ])
        checks = res["checks"]
        self.assertEqual(checks["context_reads_before_first_answer"], [])
        self.assertEqual(checks["subagents_in_grill"], ["research"])

    def test_a_skill_path_in_a_shell_variable_is_the_skill(self):
        own = "S=/x/plugin/skills/jungle-deck; cat $S/reference/context.md"
        piped = "S=/x/plugin/skills/jungle-deck; sed -n 1,9p $S/reference/x.md | grep -n migration"
        self.assertFalse(measure_run.is_context_read("Bash", {"command": piped}, piped))
        theirs = "S=/x/plugin/skills/jungle-deck; cd /r; git log --stat"
        self.assertFalse(measure_run.is_context_read("Bash", {"command": own}, own))
        self.assertTrue(measure_run.is_context_read("Bash", {"command": theirs}, theirs))

    def test_layout_runs_and_session_break_are_counted(self):
        res = self.run_on([
            START, user("네"),
            assistant("a", tool("Bash", command="python3 scripts/check_layout.py x.html"),
                      {"type": "text", "text": "새 세션에서 'jungle-deck 이어서'라고 하면 가볍게 이어져요"}),
            assistant("b", tool("Bash", command="node cdp.mjs shot.png")),
        ])
        checks = res["checks"]
        self.assertEqual(checks["check_layout_runs"], 1)
        self.assertEqual(checks["session_break_lines"], 1)
        self.assertEqual(len(checks["screenshot_tool_calls"]), 1)


if __name__ == "__main__":
    unittest.main()
