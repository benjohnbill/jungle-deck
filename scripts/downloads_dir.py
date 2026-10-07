#!/usr/bin/env python3
"""Print the default downloads folder of this machine.

The first run shows this folder to the student as the default for
`downloads_dir` in jungle-deck.local.md. pull_edits.py uses it only when
`downloads_dir` is empty.

macOS: ~/Downloads. Linux: `xdg-user-dir DOWNLOAD`, else ~/Downloads.
Windows: %USERPROFILE%\\Downloads. WSL: the Windows profile through
`wslvar USERPROFILE` or `cmd.exe` (UTF-8 code page), then `wslpath`. On
WSL with no answer, it does not guess: it exits 1 and the agent asks the
student.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def system(name, release, env):
    """'WSL', or platform.system() as is ('Linux', 'Darwin', 'Windows')."""
    if name == "Linux" and ("microsoft" in release.lower() or "WSL_DISTRO_NAME" in env):
        return "WSL"
    return name


def run(argv):
    """stdout of argv, or None when it is absent, fails, or hangs."""
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           encoding="utf-8", errors="replace", timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def windows_profile(run):
    """The Windows %USERPROFILE% seen from WSL, or None."""
    for argv in (["wslvar", "USERPROFILE"],
                 ["cmd.exe", "/c", "chcp 65001 >nul & echo %USERPROFILE%"]):
        out = (run(argv) or "").strip()
        if out and "%" not in out:
            return out
    return None


def detect(name, env, home, run):
    """The default downloads folder for system name, or None on WSL when
    the Windows profile cannot be found."""
    if name == "Windows":
        profile = env.get("USERPROFILE")
        return Path(profile) / "Downloads" if profile else home / "Downloads"
    if name == "WSL":
        profile = windows_profile(run)
        linux = (run(["wslpath", "-u", profile]) or "").strip() if profile else ""
        return Path(linux) / "Downloads" if linux else None
    if name == "Linux":
        xdg = (run(["xdg-user-dir", "DOWNLOAD"]) or "").strip()
        if xdg and Path(xdg) != home:
            return Path(xdg)
    return home / "Downloads"


def detect_here():
    env = os.environ
    return detect(system(platform.system(), platform.release(), env), env, Path.home(), run)


def main():
    found = detect_here()
    if found is None:
        print("downloads_dir: no Windows profile found from WSL; ask the student "
              "for the downloads folder", file=sys.stderr)
        return 1
    print(found)
    return 0


if __name__ == "__main__":
    sys.exit(main())
