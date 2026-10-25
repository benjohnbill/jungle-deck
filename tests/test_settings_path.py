"""Where the personal settings live (SPEC D16, 2026-10-26): outside ~/.claude,
where Claude Code asks before every edit.

Run: python3 -m unittest discover -s tests
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import publish  # noqa: E402

NEW = Path(".config") / "jungle-deck" / "jungle-deck.local.md"


class SettingsPathTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.skill = Path(tempfile.mkdtemp())
        env = {k: v for k, v in os.environ.items() if k != "JUNGLE_DECK_CONFIG"}
        self.env = mock.patch.dict(os.environ, env, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def path(self):
        with mock.patch.object(Path, "home", return_value=self.home):
            return publish.settings_path(self.skill)

    def test_default_is_under_dot_config(self):
        self.assertEqual(self.path(), self.home / NEW)

    def test_env_var_wins(self):
        os.environ["JUNGLE_DECK_CONFIG"] = str(self.skill / "x.md")
        self.assertEqual(self.path(), self.skill / "x.md")

    def test_an_old_file_in_the_skill_dir_is_read_until_migrated(self):
        (self.skill / "jungle-deck.local.md").write_text("---\n---\n", encoding="utf-8")
        self.assertEqual(self.path(), self.skill / "jungle-deck.local.md")
        (self.home / NEW).parent.mkdir(parents=True)
        (self.home / NEW).write_text("---\n---\n", encoding="utf-8")
        self.assertEqual(self.path(), self.home / NEW)


class DocsTest(unittest.TestCase):
    def test_docs_name_the_new_place_and_the_migration(self):
        text = " ".join((ROOT / "reference" / "local-template.md").read_text(encoding="utf-8").split())
        self.assertIn("~/.config/jungle-deck/jungle-deck.local.md", text)
        self.assertIn("JUNGLE_DECK_CONFIG", text)
        self.assertRegex(text, r"(?i)sensitive")
        self.assertRegex(text, r"(?i)copy .*skill directory")
        router = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("~/.config/jungle-deck/jungle-deck.local.md", router)
        self.assertNotIn("in the skill directory", router)

    def test_readme_troubleshooting_names_the_permission_prompt(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("sensitive file", readme)
        self.assertIn("bypassPermissions", readme)


if __name__ == "__main__":
    unittest.main()
