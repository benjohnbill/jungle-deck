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
            reply = mock.Mock(stdout=json.dumps({"session_id": "s", "result": ""}), returncode=0)
            with mock.patch.object(jdv.subprocess, "run", return_value=reply) as run, \
                    mock.patch("builtins.print"):
                jdv.turn(d, "hi", new=True)
        argv = run.call_args.args[0]
        self.assertNotIn("bypassPermissions", argv)
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "acceptEdits")
        allowed = argv[argv.index("--allowedTools") + 1].split()
        self.assertFalse([t for t in allowed if t.startswith("mcp")], allowed)


if __name__ == "__main__":
    unittest.main()
