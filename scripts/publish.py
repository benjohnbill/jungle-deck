#!/usr/bin/env python3
"""Publish a jungle-deck presentation to a GitHub Pages repo (SPEC D12, "Pages").

  copy    page + <slug>.assets/ -> <pages_dir>/study/[weekNN/], then byte
          compare every file. An existing file stops the copy (--replace
          republishes). The copy's back link is fitted to its depth below
          pages_dir, or dropped when pages_dir has no index.html
  verify  after the human push: poll the page URL until 200 and the live
          bytes match the published copy, check each asset URL for 200, then
          check that an index link resolves to the page URL when a card was
          expected

This script never runs git. Settings come from jungle-deck.local.md
(field meanings: reference/local-template.md).
"""

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
HOME_LINK = re.compile(rb'<a\b[^>]*\bclass="[^"]*\bhome-link\b[^"]*"[^>]*>.*?</a>', re.S)
HREF = re.compile(rb'href="[^"]*"')  # the home link's href, as the template writes it
# Any href in a hand-edited index.html: any case, double, single, or no quotes
ANY_HREF = re.compile(rb"""\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))""", re.I)
# Card markup of the built-in shape: any tag with class "card" and data-week (D12)
CARD = re.compile(rb'<\w+\b(?=[^>]*\bclass="(?:[^"]*\s)?card[\s"])(?=[^>]*\bdata-week=)[^>]*>')


class Fail(Exception):
    """A one-line reason to exit non-zero."""


def load_settings(path):
    """Read the YAML front matter of local.md as a dict of plain strings."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise Fail(f"settings file not found: {path} (run the first-run questions)")
    if not lines or lines[0].strip() != "---":
        raise Fail(f"{path}: no front matter")
    settings = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return settings
        key, sep, value = line.partition(":")
        if sep and key.strip():
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            settings[key.strip()] = value
    raise Fail(f"{path}: front matter is not closed")


def expand(path):
    return Path(path).expanduser()


def pages_dir(settings):
    """The folder GitHub Pages serves; a relative pages_dir is below pages_repo."""
    return expand(settings["pages_repo"]) / expand(settings.get("pages_dir") or ".")


def page_path(args):
    """The page's path below pages_dir: study/[weekNN/]<slug>.html (D21)."""
    week = f"week{args.week:02d}/" if args.week is not None else ""
    return f"study/{week}{args.slug}.html"


def page_bytes(deck, args, served):
    """The page as published: back link fitted to its depth, assets under the slug.

    The back link is dropped when pages_dir has no index.html (D12).
    """
    html = deck.read_bytes()
    if args.slug != deck.stem:
        html = html.replace(f"{deck.stem}.assets/".encode(), f"{args.slug}.assets/".encode())
    if not (served / "index.html").is_file():
        return HOME_LINK.sub(b"", html)
    href = b'href="' + b"../" * page_path(args).count("/") + b'"'
    return HOME_LINK.sub(lambda m: HREF.sub(href, m.group(0), count=1), html)


def published_files(deck, args, served):
    """(copy path, its bytes, source) for the page and every file in <slug>.assets/."""
    dest = served / page_path(args)
    files = [(dest, page_bytes(deck, args, served), deck)]
    assets = deck.parent / f"{deck.stem}.assets"
    if assets.is_dir():
        out = dest.parent / f"{args.slug}.assets"
        files += [(out / f.relative_to(assets), f.read_bytes(), f)
                  for f in sorted(assets.rglob("*")) if f.is_file()]
    return files


def cmd_copy(args, settings):
    deck = expand(args.deck)
    if not deck.is_file():
        raise Fail(f"deck not found: {deck}")
    pages = expand(settings["pages_repo"])
    if not pages.is_dir():
        raise Fail(f"pages_repo is not a directory: {pages}")
    if not (pages / ".git").exists():
        raise Fail(f"pages_repo is not a git repository (no .git): {pages}")
    served = pages_dir(settings)
    if not served.is_dir():
        raise Fail(f"pages_dir is not a directory: {served}")
    files = published_files(deck, args, served)
    taken = [dst for dst, _, _ in files if dst.exists()]
    if taken and not args.replace:
        raise Fail(f"path already taken: {taken[0]} (choose another slug, "
                   "or pass --replace to republish this presentation)")
    for dst, data, _ in files:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    for dst, data, src in files:
        if dst.read_bytes() != data:
            raise Fail(f"copy differs from source: {dst} != {src}")
    print(f"copied {deck} -> {files[0][0]} with {len(files) - 1} asset files")
    return 0


def fetch(url):
    """GET url; return (status, body). status is None when unreachable."""
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        e.close()
        return e.code, b""
    except (urllib.error.URLError, OSError):
        return None, b""


def url_base(settings):
    """pages_url_base, else the Pages URL from CNAME or the origin remote (SPEC "Pages")."""
    base = settings.get("pages_url_base", "")
    cname = pages_dir(settings) / "CNAME"
    if not base and cname.is_file():
        domain = cname.read_text(encoding="utf-8").strip()
        base = f"https://{domain}/" if domain else ""
    if not base:
        config = expand(settings["pages_repo"]) / ".git" / "config"
        text = config.read_text(encoding="utf-8") if config.is_file() else ""
        section = re.search(r'^\[remote "origin"\](.*?)(?=^\[|\Z)', text, re.M | re.S)
        url = re.search(r"^\s*url\s*=\s*(\S+)", section.group(1), re.M) if section else None
        repo = url and re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url.group(1))
        if not repo:
            raise Fail(f"cannot derive the Pages URL from {config}: set pages_url_base")
        owner, name = repo.group(1).lower(), repo.group(2)
        base = f"https://{owner}.github.io/"
        if name.lower() != f"{owner}.github.io":
            base += f"{name}/"
    return base if base.endswith("/") else base + "/"


def expects_card(args, served):
    """A card is added only with a week and built-in card markup in index.html (D12)."""
    index = served / "index.html"
    return args.week is not None and index.is_file() and bool(CARD.search(index.read_bytes()))


def links_to(index, index_url, page_url):
    """True when an href in index resolves to page_url: absolute, root-relative, or relative.

    Query and fragment are ignored; percent-escapes and HTML entities are decoded."""
    def page_of(url):
        parts = urllib.parse.urlsplit(url)
        return parts.scheme, parts.netloc, urllib.parse.unquote(parts.path)
    for m in ANY_HREF.finditer(index):
        raw = next(g for g in m.groups() if g is not None)
        href = unescape(raw.decode("utf-8", "replace")).strip()
        if page_of(urllib.parse.urljoin(index_url, href)) == page_of(page_url):
            return True
    return False


def live_state(page_url, asset_urls, index_url, local_page):
    """Return None when the live site is right, else the reason it is not."""
    bust = f"?v={time.time_ns()}"  # skip the Pages CDN cache (max-age 600)
    status, body = fetch(page_url + bust)
    if status != 200:
        return f"{page_url} returned {status or 'no response'}"
    if body != local_page:
        return f"live page differs from the published copy: {page_url}"
    for url in asset_urls:
        status, _ = fetch(url + bust)
        if status != 200:
            return f"asset {url} returned {status or 'no response'}"
    if index_url is None:
        return None
    status, index = fetch(index_url + bust)
    if status != 200:
        return f"index {index_url} returned {status or 'no response'}"
    if not links_to(index, index_url, page_url):
        return f"index {index_url} has no card linking {page_url}"
    return None


def cmd_verify(args, settings):
    deck = expand(args.deck)
    if not deck.is_file():
        raise Fail(f"deck not found: {deck}")
    served = pages_dir(settings)
    (_, local_page, _), *assets = published_files(deck, args, served)
    base = url_base(settings)
    page_url = base + page_path(args)
    asset_urls = [base + urllib.parse.quote(dst.relative_to(served).as_posix())
                  for dst, _, _ in assets]
    index_url = base if expects_card(args, served) else None
    start = time.monotonic()
    while True:
        reason = live_state(page_url, asset_urls, index_url, local_page)
        elapsed = time.monotonic() - start
        if reason is None:
            card = ", carded" if index_url else ""
            print(f"live and matching{card} after {elapsed:.1f} s: {page_url}")
            return 0
        if elapsed >= args.timeout:
            raise Fail(f"timeout after {elapsed:.1f} s: {reason}")
        time.sleep(min(args.interval, args.timeout - elapsed))


def parse_args(argv):
    p = argparse.ArgumentParser(prog="publish.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("copy", "verify"):
        s = sub.add_parser(name)
        s.add_argument("--deck", required=True, help="the source deck HTML")
        s.add_argument("--week", type=int,
                       help="week number, e.g. 6 or 06 (omit when the week is unknown)")
        s.add_argument("--slug", help="deck slug (default: deck file name without .html)")
        s.add_argument("--local", default=str(SKILL_ROOT / "jungle-deck.local.md"),
                       help="settings file (default: jungle-deck.local.md in the skill root)")
        if name == "copy":
            s.add_argument("--replace", action="store_true",
                           help="overwrite an earlier copy of this presentation (a republish)")
        if name == "verify":
            s.add_argument("--timeout", type=float, default=600,
                           help="seconds to wait for the live deck (default: %(default)g)")
            s.add_argument("--interval", type=float, default=10,
                           help="seconds between polls (default: %(default)g)")
    args = p.parse_args(argv)
    if not args.slug:
        args.slug = Path(args.deck).stem
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return run(args)
    except Fail as e:
        print(f"publish: {e}", file=sys.stderr)
        return 1


def run(args):
    settings = load_settings(expand(args.local))
    if not settings.get("pages_repo"):
        print(f"pages_repo is not set: publish stops at the local HTML {expand(args.deck)}")
        return 0
    return {"copy": cmd_copy, "verify": cmd_verify}[args.command](args, settings)


if __name__ == "__main__":
    sys.exit(main())
