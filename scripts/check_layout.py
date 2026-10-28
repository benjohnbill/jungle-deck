#!/usr/bin/env python3
"""Check a built presentation page for overflow and overlap, per section.

The build phase runs this once on <slug>.html (SPEC D9). It renders the page
in a headless Chrome, Chromium, or Edge at 1280x720 and 1920x1080, with every
step shown, and prints one line per <section class="slide">, then a summary.

Overflow uses the page's own check (boxesIn, overflows, measure in
templates/stage.html), the same one that marks boxes in edit mode. Overlap:
two content boxes on one slide (text, img, svg, video, canvas, iframe, real
run output) whose drawn areas cross, where neither holds the other. Small text:
SVG text that renders under MIN_FIGURE_PX, because a viewBox wider than its slot
scales every label down.

The page is copied next to the original with a measuring script added, so
relative assets resolve; the copy and the browser profile are always removed.
No browser found: one "skipped" line and exit 3 (SPEC D15).
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PureWindowsPath

SIZES = ((1280, 720), (1920, 1080))
EXIT_CLEAN, EXIT_FOUND, EXIT_ERROR, EXIT_SKIPPED = 0, 1, 2, 3
TIMEOUT_S = 60
FONT_WAIT_MS, LOAD_WAIT_MS, STOP_MS = 3000, 6000, 8000
MIN_FIGURE_PX = 12

PATH_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
              "microsoft-edge", "microsoft-edge-stable", "chrome", "msedge")
MAC_APPS = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
WIN_ROOTS = ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")
WIN_EXES = (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe",
            r"Chromium\Application\chrome.exe")

MEASURE_JS = r"""<script>
(() => {
const out = d => {
    const o = document.createElement('script');
    o.type = 'application/json'; o.id = 'jd-layout';
    o.textContent = JSON.stringify(d).replace(/</g, '\\u003c');
    document.body.appendChild(o);
};
const label = el => {
    const tag = el.tagName.toLowerCase() + (el.classList.length ? '.' + el.classList[0] : '');
    if (el.tagName === 'IMG') return tag + ' "' + (el.getAttribute('src') || '').split('/').pop() + '"';
    const text = (el.textContent || '').replace(/\s+/g, ' ').trim();
    return text ? tag + ' "' + (text.length > 30 ? text.slice(0, 30) + '…' : text) + '"' : tag;
};
/* Text counts where its lines are drawn, not its whole block box */
const drawn = el => {
    const r = document.createRange();
    r.selectNodeContents(el);
    const rs = /^(img|svg|video|canvas|iframe)$/i.test(el.tagName) ? [el.getBoundingClientRect()] : Array.from(r.getClientRects());
    return rs.filter(x => x.width > 0 && x.height > 0);
};
const cross = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > OVER_PX
    && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > OVER_PX;
function run() {
    if (![typeof boxesIn, typeof overflows, typeof measure, typeof editableIn].every(t => t === 'function'))
        return out({error: 'the page has no stage overflow check (boxesIn, overflows, measure): build it from templates/stage.html'});
    document.querySelectorAll('[data-step]').forEach(e => e.classList.add('on'));
    document.body.classList.add('jd-measure');
    const sections = Array.from(document.querySelectorAll('section.slide')).map((s, i) => {
        const overflow = boxesIn(s).filter(e => overflows(measure(e))).map(label);
        const boxes = [...new Set([...editableIn(s), ...s.querySelectorAll('img, svg, video, canvas, iframe, [data-evidence]')])]
            .filter(e => !e.closest('aside.notes') && e.getClientRects().length)
            .map(e => [e, drawn(e)]);
        const overlap = [];
        boxes.forEach(([a, ra], k) => boxes.slice(k + 1).forEach(([b, rb]) => {
            if (!a.contains(b) && !b.contains(a) && ra.some(x => rb.some(y => cross(x, y))))
                overlap.push([label(a), label(b)]);
        }));
        const small = Array.from(s.querySelectorAll('svg text'))
            .filter(t => !t.closest('aside.notes') && t.getClientRects().length && t.textContent.trim())
            .map(t => {
                const m = t.getScreenCTM();
                return [label(t), Math.round(parseFloat(getComputedStyle(t).fontSize) * (m ? Math.hypot(m.a, m.b) : 1) * 10) / 10];
            })
            .filter(([, px]) => px < MIN_FIGURE_PX);
        return {id: s.id || '#' + (i + 1), overflow, overlap, small};
    });
    const missing = document.querySelector('link[data-jd-remote][media=print]');
    out({viewport: [innerWidth, innerHeight], fonts: missing ? 'missing' : document.fonts.status, sections});
}
/* A web font that never arrives (no network) must not block the check: wait for it a little,
   then measure with the fallback font, and say so (record.fonts) */
let started = false;
const go = () => { if (!started) { started = true; run(); } };
const wait = ms => new Promise(r => setTimeout(r, ms));
addEventListener('load', () => Promise.race([document.fonts.ready, wait(FONT_WAIT_MS)]).then(go));
setTimeout(go, LOAD_WAIT_MS);
})();
</script>
"""

MEASURE_JS = (MEASURE_JS.replace("FONT_WAIT_MS", str(FONT_WAIT_MS)).replace("LOAD_WAIT_MS", str(LOAD_WAIT_MS))
              .replace("MIN_FIGURE_PX", str(MIN_FIGURE_PX)))

# An external stylesheet blocks every later script until it arrives; offline, that is never.
# In the measuring copy it loads without blocking (the page itself is unchanged).
REMOTE_CSS = re.compile(r'<link\b(?=[^>]*\brel=["\']?stylesheet)(?=[^>]*\bhref=["\']?(?:https?:)?//)[^>]*?/?>', re.I)

RECORD = re.compile(r'<script type="application/json" id="jd-layout">(.*?)</script>', re.S)


class LayoutError(Exception):
    pass


def is_wsl():
    try:
        with open("/proc/sys/kernel/osrelease") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def windows_env_from_wsl():
    """The WIN_ROOTS variables of Windows, as WSL paths, read through cmd.exe."""
    try:
        out = subprocess.run(["cmd.exe", "/c", "echo " + ";".join("%" + r + "%" for r in WIN_ROOTS)],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding="utf-8",
                             errors="replace", cwd="/", timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return {}
    env = {}
    for root, value in zip(WIN_ROOTS, out.split(";")):
        if value and not value.startswith("%"):
            unix = subprocess.run(["wslpath", "-u", value], stdout=subprocess.PIPE, encoding="utf-8")
            if unix.stdout.strip():
                env[root] = unix.stdout.strip()
    return env


def find_browser(system=None, env=None, is_file=os.path.isfile, which=shutil.which, wsl=None):
    """Path of a Chromium-family browser, or None. Firefox cannot dump the DOM after scripts run.
    On WSL with no Linux browser, the Windows one: Edge ships with every Windows."""
    system = system or platform.system()
    wsl = is_wsl() if wsl is None else wsl
    env = os.environ if env is None else env
    for name in PATH_NAMES:
        found = which(name)
        if found:
            return found
    if system == "Darwin":
        candidates = list(MAC_APPS) + [str(Path.home()) + app for app in MAC_APPS]
    elif system == "Windows":
        candidates = [str(PureWindowsPath(env[root], exe)) for root in WIN_ROOTS if env.get(root) for exe in WIN_EXES]
    elif wsl:
        roots = windows_env_from_wsl() if env is os.environ else env
        candidates = [roots[r] + "/" + exe.replace("\\", "/") for r in WIN_ROOTS if roots.get(r) for exe in WIN_EXES]
    else:
        candidates = []
    return next((c for c in candidates if is_file(c)), None)


def parse_dump(text):
    """The measuring script's record from a --dump-dom output."""
    m = RECORD.search(text)
    if not m:
        raise LayoutError("the browser returned no measurement (did the page finish loading?)")
    data = json.loads(m.group(1))
    if "error" in data:
        raise LayoutError(data["error"])
    return data


def report(measurements):
    """Lines to print and the exit code, from [(size label, record)] in size order."""
    found = {}
    for size, data in measurements:
        for sec in data["sections"]:
            items = found.setdefault(sec["id"], [])
            if sec["overflow"]:
                items.append("overflow %s: %s" % (size, ", ".join(sec["overflow"])))
            if sec["overlap"]:
                items.append("overlap %s: %s" % (size, ", ".join("%s × %s" % tuple(p) for p in sec["overlap"])))
            if sec.get("small"):
                items.append("small text %s: %s" % (size, ", ".join("%s %gpx" % tuple(t) for t in sec["small"])))
    lines = ["%s  %s" % (sid, "; ".join(items) if items else "ok") for sid, items in found.items()]
    if any(data.get("fonts", "loaded") != "loaded" for _, data in measurements):
        lines.append("note: a web font or an external stylesheet did not load; measured with the fallback font")
    bad = [sid for sid, items in found.items() if items]
    sizes = " and ".join(size for size, _ in measurements)
    if bad:
        lines.append("%d of %d sections need a fix: %s" % (len(bad), len(found), ", ".join(bad)))
    else:
        lines.append("all %d sections fit at %s, no overlap, no small figure text" % (len(found), sizes))
    return lines, EXIT_FOUND if bad else EXIT_CLEAN


def render(browser, url, window, profile):
    """The record of one headless render with the window at `window` (w, h)."""
    argv = [browser, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
            "--hide-scrollbars", "--user-data-dir=" + profile, "--window-size=%d,%d" % window,
            "--virtual-time-budget=10000", "--timeout=%d" % STOP_MS, "--dump-dom", url]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        argv.insert(1, "--no-sandbox")
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           encoding="utf-8", errors="replace", timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise LayoutError("the browser did not finish in %d s" % TIMEOUT_S)
    except OSError as e:
        raise LayoutError("cannot start %s: %s" % (browser, e))
    return parse_dump(p.stdout)


def measure_at(browser, url, size, profile):
    """The record at viewport `size`. Headless window chrome takes some height, so a
    first render finds the gap and a second one closes it."""
    data = render(browser, url, size, profile)
    got = tuple(data["viewport"])
    if got != size:
        data = render(browser, url, (2 * size[0] - got[0], 2 * size[1] - got[1]), profile)
        if tuple(data["viewport"]) != size:
            raise LayoutError("viewport is %dx%d, not %dx%d" % (tuple(data["viewport"]) + size))
    return data


def wsl_windows_path(path):
    out = subprocess.run(["wslpath", "-w", str(path)], stdout=subprocess.PIPE, encoding="utf-8", check=True)
    return out.stdout.strip()


def wsl_windows_temp():
    """A WSL path to the Windows %TEMP%: a Windows browser keeps its profile there."""
    out = subprocess.run(["cmd.exe", "/c", "echo %TEMP%"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace", cwd="/")
    unix = subprocess.run(["wslpath", "-u", out.stdout.strip()], stdout=subprocess.PIPE, encoding="utf-8")
    return unix.stdout.strip() or None


def check(page, browser):
    html = REMOTE_CSS.sub(lambda m: m.group(0)[:-1].rstrip("/") + ' data-jd-remote media="print" onload="this.media=\'all\'">',
                          page.read_text(encoding="utf-8"))
    at = html.lower().rfind("</body>")
    html = html[:at] + MEASURE_JS + html[at:] if at >= 0 else html + MEASURE_JS
    fd, copy = tempfile.mkstemp(prefix="." + page.stem + ".check-", suffix=".html", dir=str(page.parent))
    windows_browser = browser.lower().endswith(".exe") and platform.system() != "Windows"
    profile = tempfile.mkdtemp(prefix="jd-check-", dir=wsl_windows_temp() if windows_browser else None)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html)
        if windows_browser:
            url = PureWindowsPath(wsl_windows_path(Path(copy).resolve())).as_uri()
            browser_profile = wsl_windows_path(profile)
        else:
            url, browser_profile = Path(copy).resolve().as_uri(), profile
        return [("%dx%d" % size, measure_at(browser, url, size, browser_profile)) for size in SIZES]
    finally:
        os.remove(copy)
        shutil.rmtree(profile, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check_layout.py",
        description="Render a built presentation page headless at 1280x720 and 1920x1080 with every "
                    "step shown. Print one line per section (ok, or each overflowing box and each "
                    "overlapping pair with the size), then a summary.",
        epilog="exit codes: 0 every section fits, 1 overflow, overlap, or small figure text found, 2 error, "
               "3 skipped: no headless browser (Chrome, Chromium, or Edge)")
    ap.add_argument("page", help="the built page, <slug>.html")
    ap.add_argument("--browser", metavar="PATH", help="Chrome, Chromium, or Edge to use (default: search)")
    args = ap.parse_args(argv)
    page = Path(args.page)
    if not page.is_file():
        print("error: no such page: %s" % page, file=sys.stderr)
        return EXIT_ERROR
    browser = args.browser or find_browser()
    if not browser:
        print("skipped: no headless browser (Chrome, Chromium, or Edge); the student preview is the check")
        return EXIT_SKIPPED
    try:
        lines, code = report(check(page, browser))
    except LayoutError as e:
        print("error: %s" % e, file=sys.stderr)
        return EXIT_ERROR
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
