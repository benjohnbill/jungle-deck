#!/usr/bin/env python3
"""Revise server: serve one presentation and save the page's edits (SPEC D11).

Serves http://127.0.0.1:<port>/<slug>.html from the save folder. On Ctrl+S
the page POSTs the sections it changed, with the hash of the version it
loaded. A section is written only when the source still holds what that
version held (a three-way merge per section id); any clash writes nothing,
answers 409, and keeps the payload in _backup/rejected-<stamp>.json.

Stdlib only, Python 3.8+. Binds 127.0.0.1 only.

  <python_cmd> scripts/serve.py --deck <save folder>/<slug>.html
"""

import argparse
import hashlib
import json
import os
import re
import socket
import sys
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pull_edits  # noqa: E402  (sections, clean, backup, write_atomic)

PORT_BASE, PORT_SPAN = 47000, 1000
MAX_BODY = 5 * 1024 * 1024
MAX_SNAPSHOTS = 100   # an older base_hash gets 409, which keeps the student's text
SAVE_PATH = "/save"
SAVE_HEADER = ("X-Jungle-Deck", "save")   # a custom header forces a CORS preflight
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".gif": "image/gif", ".webp": "image/webp", ".avif": "image/avif"}
# No .svg: an SVG opened on this origin could run script and POST /save.
HEAD = re.compile(r"<head\b[^>]*>", re.I)


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def first_port(slug):
    return PORT_BASE + zlib.crc32(slug.encode("utf-8")) % PORT_SPAN


def inject_base(html, h):
    """Put the jd-base meta right after <head> (served copy only, never on disk)."""
    meta = f'<meta name="jd-base" content="{h}">'
    m = HEAD.search(html)
    if not m:
        return meta + html
    return html[:m.end()] + "\n" + meta + html[m.end():]


class Server(ThreadingHTTPServer):
    allow_reuse_address = False   # a busy port must fail, on every OS

    def __init__(self, deck, port):
        self.deck = deck
        self.folder = deck.parent
        self.slug = deck.stem
        self.port = port
        self.lock = threading.Lock()
        self.snapshots = {}
        self.current()            # seed the snapshot with the file at startup
        super().__init__(("127.0.0.1", port), Handler)

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):   # Windows
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def current(self):
        """The source text and its hash; every version read is kept as a snapshot."""
        text = pull_edits.read_keeping_newlines(self.deck)
        h = content_hash(text)
        self.snapshots.pop(h, None)        # re-insert: the newest stays last
        self.snapshots[h] = text
        while len(self.snapshots) > MAX_SNAPSHOTS:
            del self.snapshots[next(iter(self.snapshots))]
        return text, h

    def save(self, payload):
        """Three-way save of the sent sections; return (status, reply object)."""
        base_hash, sent = payload.get("base_hash"), payload.get("sections")
        if not isinstance(base_hash, str) or not isinstance(sent, dict) or \
                not all(isinstance(v, str) for v in sent.values()):
            return 400, {"error": "need base_hash and sections {id: html}"}
        with self.lock:
            text, h = self.current()
            base = self.snapshots.get(base_hash)
            src = dict(pull_edits.sections(text))
            if base is None:
                conflicts = sorted(sent)
            else:
                old = {i: m.group(2) for i, m in pull_edits.sections(base)}
                conflicts = sorted(i for i in sent
                                   if i not in src or old.get(i) != src[i].group(2))
            if conflicts:
                kept = self.reject(payload)
                self.log(f"409 {','.join(conflicts)} payload={kept}")
                return 409, {"conflicts": conflicts, "payload": str(kept)}
            edits = []
            for i, inner in sent.items():
                m = src[i]
                new = pull_edits.lf(pull_edits.clean(inner))
                if "\r\n" in text:
                    new = new.replace("\n", "\r\n")
                if not pull_edits.same(pull_edits.clean(m.group(2)), new):
                    edits.append((m.start(2), m.end(2), new, i))
            # Whether the file held the client's base just before this save.
            # False: it also holds edits the page does not show, so the page
            # keeps its old base instead of adopting the new hash.
            current = h == base_hash
            if not edits:
                self.log("save (no change)")
                return 200, {"hash": h, "written": [], "base_current": current}
            out = text
            for start, end, new, _ in sorted(edits, reverse=True):
                out = out[:start] + new + out[end:]
            copy = pull_edits.backup(self.deck)
            pull_edits.write_atomic(self.deck, out)
            _, h = self.current()
            ids = [i for *_, i in edits]
            self.log(f"save {','.join(ids)} backup={copy}")
            return 200, {"hash": h, "written": ids, "base_current": current}

    def reject(self, payload):
        """Keep a rejected payload in _backup/rejected-<stamp>.json; return its path."""
        folder = self.folder / "_backup"
        folder.mkdir(exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        dest, n = folder / f"rejected-{stamp}.json", 1
        while dest.exists():
            dest, n = folder / f"rejected-{stamp}-{n}.json", n + 1
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        return dest

    def log(self, line):
        with open(self.folder / ".serve.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {line}\n")

    def asset(self, rel):
        """The image file under <slug>.assets/ for rel, or None."""
        parts = rel.split("/")
        if any(p.startswith(".") or not p for p in parts):
            return None
        # The root is not resolved: a symlinked assets folder is refused too.
        root = self.folder.resolve() / f"{self.slug}.assets"
        path = (root / rel).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return None
        if path.suffix.lower() not in IMAGE_TYPES or not path.is_file():
            return None
        return path


class Handler(BaseHTTPRequestHandler):
    server_version = "jungle-deck-serve"

    def log_message(self, fmt, *args):
        pass

    def host_ok(self):
        port = self.server.port
        if self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}"):
            return True
        self.reply(403, {"error": "bad host"})
        return False

    def reply(self, status, obj=None, body=None, ctype="application/json"):
        if body is None:
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.host_ok():
            return
        s = self.server
        path = unquote(urlsplit(self.path).path)
        if path == f"/{s.slug}.html":
            with s.lock:
                text, h = s.current()
            self.reply(200, body=inject_base(text, h).encode("utf-8"),
                       ctype="text/html; charset=utf-8")
        elif path == "/version":
            with s.lock:
                _, h = s.current()
            self.reply(200, {"slug": s.slug, "source": str(s.deck.resolve()), "hash": h})
        else:
            prefix = f"/{s.slug}.assets/"
            f = s.asset(path[len(prefix):]) if path.startswith(prefix) else None
            if f:
                self.reply(200, body=f.read_bytes(), ctype=IMAGE_TYPES[f.suffix.lower()])
            else:
                self.reply(404, {"error": "not found"})


    def do_OPTIONS(self):
        # No CORS headers ever: a cross-origin preflight always fails.
        if self.host_ok():
            self.reply(405, {"error": "method not allowed"})

    def do_POST(self):
        if not self.host_ok():
            return
        port = self.server.port
        self.close_connection = True
        if urlsplit(self.path).path != SAVE_PATH:
            return self.reply(404, {"error": "not found"})
        if self.headers.get("Origin") not in (f"http://127.0.0.1:{port}",
                                              f"http://localhost:{port}") \
                or self.headers.get(SAVE_HEADER[0]) != SAVE_HEADER[1]:
            return self.reply(403, {"error": "bad origin or missing header"})
        if self.headers.get_content_type() != "application/json":
            return self.reply(415, {"error": "need application/json"})
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self.reply(411, {"error": "need Content-Length"})
        if length < 0:
            return self.reply(400, {"error": "bad Content-Length"})
        if length > MAX_BODY:
            return self.reply(413, {"error": "body over 5 MB"})
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self.reply(400, {"error": "body is not JSON"})
        if not isinstance(payload, dict):
            return self.reply(400, {"error": "body is not a JSON object"})
        self.reply(*self.server.save(payload))


def make_server(deck):
    """Bind the first free port from 47000 + crc32(slug) % 1000; write .serve.json."""
    deck = Path(deck).resolve()
    start = first_port(deck.stem)
    for i in range(PORT_SPAN):
        port = PORT_BASE + (start - PORT_BASE + i) % PORT_SPAN
        try:
            server = Server(deck, port)
        except OSError:
            continue
        (deck.parent / ".serve.json").write_text(
            json.dumps({"port": port, "pid": os.getpid()}) + "\n", encoding="utf-8")
        return server
    raise OSError(f"no free port in {PORT_BASE}-{PORT_BASE + PORT_SPAN - 1}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deck", required=True, type=Path, help="<save folder>/<slug>.html")
    args = ap.parse_args(argv)
    if not args.deck.is_file():
        print(f"serve: no such file: {args.deck}", file=sys.stderr)
        return 1
    try:
        server = make_server(args.deck)
    except OSError as e:
        print(f"serve: {e}", file=sys.stderr)
        return 1
    print(f"serving http://127.0.0.1:{server.port}/{server.slug}.html", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
