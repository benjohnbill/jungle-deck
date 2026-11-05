"""tools/verify/repo_state.py must fail on a state it claims to catch.

Run: python3 -m unittest discover -s tests
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "verify"))
import repo_state  # noqa: E402


class LocalChecksTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "t")
        self.git("config", "user.email", "t@example.com")
        self.commit("cases/a.md", "clean\n")

    def git(self, *argv):
        subprocess.run(["git", *argv], cwd=str(self.repo), check=True, capture_output=True)

    def commit(self, path, text):
        (self.repo / path).parent.mkdir(exist_ok=True)
        (self.repo / path).write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "x")

    def test_dirty_tree_fails(self):
        self.assertEqual(repo_state.working_tree(self.repo)[0], repo_state.PASS)
        (self.repo / "new").write_text("x", encoding="utf-8")
        self.assertEqual(repo_state.working_tree(self.repo)[0], repo_state.FAIL)

    def test_a_name_removed_later_is_still_found(self):
        hashes = {repo_state.check_cases.digest("zorblax")}
        self.assertEqual(repo_state.name_history(self.repo, hashes)[0], repo_state.PASS)
        self.commit("cases/a.md", "by zorblax\n")
        self.commit("cases/a.md", "clean\n")
        self.assertEqual(repo_state.name_history(self.repo, hashes)[0], repo_state.FAIL)

    def test_no_upstream_is_a_skip_not_a_pass(self):
        self.assertEqual(repo_state.pushed(self.repo)[0], repo_state.SKIP)


if __name__ == "__main__":
    unittest.main()
