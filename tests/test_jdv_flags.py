"""tools/verify/jdv.py must never open every tool to a live agent.

A bypassPermissions flag shipped in f5b7717 unnoticed: the revert sat in a
refused command. This test reads the argv that `turn` really passes.

Run: python3 -m unittest discover -s tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "verify"))
import jdv  # noqa: E402


class TurnFlagsTest(unittest.TestCase):
    def test_turn_runs_accept_edits_with_no_mcp_tool(self):
        with tempfile.TemporaryDirectory() as d:
            jdv.save(d, {"rev": "x", "plugin": d, "repo": d, "sessions": [], "turns": []})
            proc = mock.Mock(returncode=0, pid=1)
            proc.poll.return_value = 0
            proc.communicate.return_value = (json.dumps({"session_id": "s", "result": ""}), "")
            with mock.patch.object(jdv.subprocess, "Popen", return_value=proc) as popen, \
                    mock.patch("builtins.print"):
                jdv.turn(d, "hi", new=True)
        argv = popen.call_args.args[0]
        self.assertNotIn("bypassPermissions", argv)
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "acceptEdits")
        allowed = argv[argv.index("--allowedTools") + 1].split()
        self.assertFalse([t for t in allowed if t.startswith("mcp")], allowed)
        self.assertIn("--session-id", argv)

    def test_a_final_reply_is_read_from_the_transcript(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d) / "s.jsonl"
            done = {"type": "assistant", "message": {"stop_reason": "end_turn",
                                                     "content": [{"type": "text", "text": "끝"}]}}
            t.write_text(json.dumps({"type": "user", "message": {"content": "hi"}}) + "\n", encoding="utf-8")
            self.assertIsNone(jdv.last_reply(t)[0])
            t.write_text(t.read_text(encoding="utf-8") + json.dumps(done) + "\n", encoding="utf-8")
            self.assertEqual(jdv.last_reply(t)[0], "끝")


class SeedTest(unittest.TestCase):
    def test_seed_resets_design_and_keeps_grill_and_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            src, run = tmp / "src", tmp / "run"
            talk = src / "week09" / "talk"
            (talk / "previews").mkdir(parents=True)
            (talk / "previews" / "a.html").write_text("x", encoding="utf-8")
            (talk / "talk.html").write_text("x", encoding="utf-8")
            (talk / "evidence.txt").write_text("real", encoding="utf-8")
            (talk / "BRIEF.md").write_text(
                "---\nphase: build\nsource_repo: %s/week09\n---\n## Next action\n\nSTALE\n\n"
                "## Grill\n\nthesis\n\n## Design\n\n- Source: STALE\n\n## Build\n\n- Page file: STALE\n\n"
                "## Revise\n\nr\n" % src, encoding="utf-8")
            reference = run / "plugin" / "skills" / "jungle-deck" / "reference"
            reference.mkdir(parents=True)
            (reference / "brief-template.md").write_text(
                "## Design\n\n- Source: TBD\n\n## Build\n\n- Page file: TBD\n\n## Revise\n", encoding="utf-8")
            for settings in (run / "jungle-deck.local.md", reference.parent / "jungle-deck.local.md"):
                settings.write_text('current_brief: ""\n', encoding="utf-8")
            (run / "week09").mkdir()
            jdv.save(run, {"rev": "x", "plugin": "", "repo": "", "sessions": [], "turns": []})
            with mock.patch("builtins.print"):
                jdv.seed(run, src)
            talk = run / "week09" / "talk"
            text = (talk / "BRIEF.md").read_text(encoding="utf-8")
            self.assertIn("phase: design", text)
            self.assertIn("source_repo: %s/week09" % run.resolve(), text)
            self.assertIn("thesis", text)
            self.assertIn("- Source: TBD", text)
            self.assertIn("- Page file: TBD", text)
            self.assertNotIn("STALE", text)
            self.assertEqual(sorted(p.name for p in talk.iterdir()), ["BRIEF.md", "evidence.txt"])
            self.assertIn(str(talk / "BRIEF.md"), (run / "jungle-deck.local.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
