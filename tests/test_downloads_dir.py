"""Tests for scripts/downloads_dir.py: the default downloads folder per OS.

Run: python3 -m unittest discover -s tests
Every OS is faked through arguments, so the suite runs on any host.
"""

import contextlib
import importlib.util
import io
import sys
import unittest
import unittest.mock
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("downloads_dir", ROOT / "scripts" / "downloads_dir.py")
downloads_dir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloads_dir)

HOME = Path("/home/student")


def fake_run(answers):
    """A run() that answers argv[0] from answers; other commands are absent."""
    calls = []

    def run(argv):
        calls.append(argv)
        return answers.get(argv[0])
    run.calls = calls
    return run


class System(unittest.TestCase):
    def test_wsl_is_linux_with_a_microsoft_kernel(self):
        self.assertEqual(downloads_dir.system("Linux", "6.18.40.1-microsoft-standard-WSL2", {}), "WSL")

    def test_wsl_is_also_found_by_its_env(self):
        self.assertEqual(downloads_dir.system("Linux", "5.15.0", {"WSL_DISTRO_NAME": "Ubuntu"}), "WSL")

    def test_plain_linux_mac_and_windows(self):
        self.assertEqual(downloads_dir.system("Linux", "6.8.0-45-generic", {}), "Linux")
        self.assertEqual(downloads_dir.system("Darwin", "24.0.0", {}), "Darwin")
        self.assertEqual(downloads_dir.system("Windows", "11", {}), "Windows")


class Detect(unittest.TestCase):
    def detect(self, system, env=None, answers=None):
        return downloads_dir.detect(system, env or {}, HOME, fake_run(answers or {}))

    def test_mac_uses_home_downloads(self):
        self.assertEqual(self.detect("Darwin"), HOME / "Downloads")

    def test_linux_asks_xdg_first(self):
        got = self.detect("Linux", answers={"xdg-user-dir": "/home/student/다운로드\n"})
        self.assertEqual(got, Path("/home/student/다운로드"))

    def test_linux_without_xdg_uses_home_downloads(self):
        self.assertEqual(self.detect("Linux"), HOME / "Downloads")

    def test_linux_xdg_answering_home_means_unset(self):
        # xdg-user-dir prints $HOME when the folder is not configured.
        self.assertEqual(self.detect("Linux", answers={"xdg-user-dir": f"{HOME}\n"}), HOME / "Downloads")

    def test_windows_uses_userprofile(self):
        got = self.detect("Windows", env={"USERPROFILE": r"C:\Users\학생"})
        self.assertEqual(PureWindowsPath(got), PureWindowsPath(r"C:\Users\학생\Downloads"))

    def test_windows_without_userprofile_uses_home(self):
        self.assertEqual(self.detect("Windows"), HOME / "Downloads")

    def test_wsl_uses_wslvar_then_wslpath(self):
        run = fake_run({"wslvar": "C:\\Users\\Student\r\n", "wslpath": "/mnt/c/Users/Student\n"})
        got = downloads_dir.detect("WSL", {"USER": "student"}, HOME, run)
        self.assertEqual(got, Path("/mnt/c/Users/Student/Downloads"))
        self.assertEqual(run.calls[-1], ["wslpath", "-u", "C:\\Users\\Student"])

    def test_wsl_falls_back_to_cmd_exe(self):
        run = fake_run({"cmd.exe": "C:\\Users\\Student\r\n", "wslpath": "/mnt/c/Users/Student\n"})
        got = downloads_dir.detect("WSL", {}, HOME, run)
        self.assertEqual(got, Path("/mnt/c/Users/Student/Downloads"))

    def test_wsl_unexpanded_variable_is_no_answer(self):
        run = fake_run({"cmd.exe": "%USERPROFILE%\r\n", "wslpath": "/mnt/c/x\n"})
        self.assertIsNone(downloads_dir.detect("WSL", {}, HOME, run))

    def test_wsl_without_answers_does_not_guess(self):
        self.assertIsNone(self.detect("WSL", env={"USER": "student"}))


class Run(unittest.TestCase):
    def test_non_utf8_stderr_does_not_break_stdout(self):
        # cmd.exe from WSL writes a CP949 UNC warning to stderr.
        out = downloads_dir.run([sys.executable, "-c",
                                 "import sys; sys.stdout.write('C:/Users/S'); "
                                 "sys.stderr.buffer.write(bytes([0xc0, 0xaf]))"])
        self.assertEqual(out, "C:/Users/S")

    def test_absent_command_is_none(self):
        self.assertIsNone(downloads_dir.run(["no-such-command-jungle-deck"]))


class Cli(unittest.TestCase):
    def run_main(self, found):
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(downloads_dir, "detect", return_value=found), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = downloads_dir.main()
        return code, out.getvalue(), err.getvalue()

    def test_prints_the_folder(self):
        code, out, err = self.run_main(Path("/mnt/c/Users/Student/Downloads"))
        self.assertEqual((code, out.strip(), err), (0, "/mnt/c/Users/Student/Downloads", ""))

    def test_no_folder_exits_non_zero_and_says_ask(self):
        code, out, err = self.run_main(None)
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("ask", err)


if __name__ == "__main__":
    unittest.main()
