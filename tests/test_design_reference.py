"""Contract checks for reference/design.md (SPEC D14, D17, D25; issues #20, #27).

The mapping test reads the token chains from the table in design.md and
applies them, so it checks the document, not a copy of it.
The network test fetches every getdesign.md file (about 85 requests). It
runs only with JD_NETWORK=1 and skips when GitHub is not reachable.

Run: python3 -m unittest discover -s tests
"""
import colorsys
import json
import os
import re
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "reference" / "design.md"
BRIEF = ROOT / "reference" / "brief-template.md"
STAGE = ROOT / "templates" / "stage.html"

RAW = "https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/"
TREE = ("https://api.github.com/repos/VoltAgent/awesome-design-md/"
        "git/trees/main?recursive=1")

# SPEC D25, in order.
D25_CHAINS = {
    "--paper": ["canvas"],
    "--ink": ["ink"],
    "--acc": ["primary"],
    "--mut": ["ink-mute", "ink-muted", "muted", "mute", "ink-subtle", "body"],
    "--panel": ["canvas-soft", "surface-soft", "surface-1", "surface"],
    "--grid": ["hairline", "hairline-soft"],
}


def section(text, heading):
    """Return the body of the `## heading` section, up to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)",
                  text, re.S | re.M)
    if not m:
        raise AssertionError(f"no '## {heading}' section")
    return m.group(1)


def flat(text):
    """Collapse line wraps so a phrase can span two lines."""
    return re.sub(r"\s+", " ", text)


def doc_chains(text):
    """The mapping table of design.md as {token: [keys]}."""
    chains = {}
    for tok, keys in re.findall(r"^\| `(--[\w-]+)` \| (.+?) \|$",
                                section(text, "Token mapping"), re.M):
        chains[tok] = re.findall(r"`([\w-]+)`", keys)
    return chains


def empty_chain_values(text):
    """The `color-mix()` fallbacks of the Empty chain list as {token: css}."""
    return dict(re.findall(r"^- `(--[\w-]+)`: `(color-mix\([^`]+\))`$",
                           section(text, "Token mapping"), re.M))


def template_value(token):
    m = re.search(rf"^\s*{re.escape(token)}:\s*([^;]+);",
                  STAGE.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip()


# --- the mapping, as design.md states it ---------------------------------

VALUE = re.compile(r"""^\s+([\w.-]+):\s*(?:"([^"]*)"|'([^']*)'|([^\s#]\S*))"""
                   r"""\s*(?:#.*)?$""")


def front_colors(text):
    """`colors:` of the YAML front matter, or None when there is none."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    colors, inside = {}, False
    for line in text[4:end].splitlines():
        if re.match(r"^colors:\s*(#.*)?$", line):
            inside = True
        elif inside and line.strip() and not line[0].isspace():
            break
        elif inside:
            m = VALUE.match(line)
            if m:
                colors[m.group(1)] = next(g for g in m.groups()[1:]
                                          if g is not None)
    return colors


def rgb(value):
    m = re.fullmatch(r"#([0-9a-fA-F]{6})|#([0-9a-fA-F]{3})", value.strip())
    if not m:
        return None
    h = m.group(1) or "".join(c * 2 for c in m.group(2))
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def contrast(a, b):
    def lum(c):
        r, g, b_ = (x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
                    for x in c)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b_
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def saturated(c):
    _, light, sat = colorsys.rgb_to_hls(*c)
    return sat >= 0.4 and 0.2 <= light <= 0.8


FALLBACK_ACCENT = "#3b82f6"


def map_tokens(colors, text):
    """Apply the Token mapping section of design.md (`text`).
    Returns ({token: css value}, the color key the accent came from);
    the key is None when the fallback accent was used."""
    derived = empty_chain_values(text)
    out = {}
    for tok, keys in doc_chains(text).items():
        hit = next((colors[k] for k in keys if k in colors), None)
        out[tok] = hit or derived.get(tok) or template_value(tok)
    ink, paper = rgb(out["--ink"]), rgb(out["--paper"])

    def readable(c):
        return bool(c) and c != ink and contrast(c, paper) >= 3

    def passes(key):
        c = rgb(colors[key])
        return readable(c) and saturated(c)

    if "primary" in colors and readable(rgb(colors["primary"])):
        return out, "primary"
    keys = list(colors)
    order = ([k for k in keys if k == "link" or k.startswith("link-")]
             + [k for k in keys if k.startswith("brand-")]
             + [k for k in keys if k.startswith("accent")]
             + keys)
    key = next((k for k in order if passes(k)), None)
    out["--acc"] = colors[key] if key else FALLBACK_ACCENT
    return out, key


# --- contract checks --------------------------------------------------------

class DesignReferenceTest(unittest.TestCase):
    def setUp(self):
        self.text = DESIGN.read_text(encoding="utf-8")

    def test_front_matter_has_scope_authority_status(self):
        head = self.text.split("\n---", 1)[0]
        for key in ("scope:", "authority:", "status:"):
            self.assertIn(key, head)

    def test_d17_steps_in_order(self):
        body = flat(section(self.text, "Steps"))
        marks = [
            "이번에도 이 스타일로 갈까요?",
            "원하는 디자인 레퍼런스가 있어요? (사이트 URL, 이미지, DESIGN.md)",
            "getdesign.md 레퍼런스 중에서 고를까요?",
            "The student's reference",
            "A getdesign.md pick",
            "`frontend-slides` style discovery",
            "vendor/frontend-slides/STYLE_PRESETS.md",
            "Previews, then the accent",
            "Record and confirm",
            "Set `phase: build` only after the student says yes",
        ]
        positions = [body.index(m) for m in marks]
        self.assertEqual(positions, sorted(positions))

    def test_dark_canvas_is_warned_and_allowed(self):
        body = flat(section(self.text, "Steps"))
        self.assertIn("A dark canvas", body)
        self.assertIn("If the student keeps it, use it", body)

    def test_design_section_fields_match_brief_template(self):
        brief = section(BRIEF.read_text(encoding="utf-8"), "Design")
        body = section(self.text, "The Design section")
        for field in ("Source", "Tokens", "Accent"):
            self.assertIn(f"- {field}:", brief)
            self.assertIn(f"`{field}`", body)
        self.assertIn("D14", body)

    def test_getdesign_listing_uses_raw_urls(self):
        body = flat(section(self.text, "getdesign.md references"))
        self.assertIn(RAW + "README.md", body)
        self.assertIn(RAW + "design-md/<brand>/DESIGN.md", body)
        self.assertIn("https://getdesign.md/<brand>/design-md", body)
        self.assertIn("no `npx`", body)
        self.assertIn("not in the repo", body)

    def test_no_front_matter_is_the_students_own_reference(self):
        body = flat(section(self.text, "getdesign.md references"))
        self.assertIn("no front matter", body)
        self.assertIn("not recommended", body)
        self.assertIn("treat it as the student's own reference", body)

    def test_color_and_type_mood_message_comes_first(self):
        body = flat(section(self.text, "getdesign.md references"))
        self.assertIn("Say this first", body)
        self.assertIn("색과 글꼴 분위기만", body)
        self.assertIn("frontend-slides 프리셋", body)

    def test_mapping_table_equals_d25_chains(self):
        self.assertEqual(doc_chains(self.text), D25_CHAINS)

    def test_empty_chain_and_accent_rule(self):
        body = flat(section(self.text, "Token mapping"))
        for tok in ("--mut", "--panel", "--grid"):
            self.assertRegex(body, rf"`{tok}`: `color-mix\(")
        self.assertIn("contrast below 3:1 against `paper`", body)
        self.assertIn("`link`, `link-*`, `brand-*`, `accent*`", body)
        self.assertIn("3:1 or more against `paper`", body)
        self.assertNotIn("against `ink`", body)
        self.assertIn(f"No color passes: use `{FALLBACK_ACCENT}`", body)
        self.assertIn("mid-tone paper", body)
        self.assertEqual(set(empty_chain_values(self.text)),
                         {"--mut", "--panel", "--grid"})
        self.assertIn("Ask the student to confirm the accent", body)

    def test_fonts_keep_template_sizes(self):
        body = flat(section(self.text, "Token mapping"))
        self.assertIn("font family only", body)
        self.assertIn("Korean font", body)
        self.assertIn("`clamp()` sizes", body)
        for key in ("fontWeight", "letterSpacing", "lineHeight"):
            self.assertIn(key, body)

    def test_mapped_tokens_exist_in_stage_template(self):
        for tok in D25_CHAINS:
            self.assertTrue(template_value(tok))

    def test_named_paths_exist(self):
        for path in re.findall(r"`((?:reference|templates|vendor)/[\w./-]+)`",
                               self.text):
            self.assertTrue((ROOT / path).exists(), path)


class MappingTest(unittest.TestCase):
    """The mapping on small fixtures, offline."""

    def setUp(self):
        self.text = DESIGN.read_text(encoding="utf-8")

    def colors_of(self, body):
        return front_colors("---\nname: x\ncolors:\n" + body + "---\n# x\n")

    def test_first_present_key_wins_and_comments_are_dropped(self):
        colors = self.colors_of('  canvas: "#fafafa"  # page\n'
                         '  ink: "#101010"\n  primary: "#ff5500"\n'
                         '  muted: "#777777"\n  ink-mute: "#666666"\n')
        out, src = map_tokens(colors, self.text)
        self.assertEqual(out["--paper"], "#fafafa")
        self.assertEqual(out["--mut"], "#666666")
        self.assertTrue(out["--panel"].startswith("color-mix("))
        self.assertEqual(src, "primary")

    def test_primary_equal_to_ink_takes_link(self):
        colors = self.colors_of('  ink: "#000000"\n  primary: "#000000"\n'
                         '  brand-red: "#dd2222"\n  link: "#0055ee"\n')
        out, src = map_tokens(colors, self.text)
        self.assertEqual((out["--acc"], src), ("#0055ee", "link"))

    def test_no_saturated_color_keeps_template_accent(self):
        colors = self.colors_of('  ink: "#000000"\n  primary: "#000000"\n')
        out, src = map_tokens(colors, self.text)
        self.assertEqual((out["--acc"], src), (FALLBACK_ACCENT, None))

    def test_primary_close_to_ink_is_kept_when_it_reads_on_paper(self):
        # stripe: a saturated primary that is dark like the ink (#27).
        colors = self.colors_of('  canvas: "#ffffff"\n  ink: "#0d253d"\n'
                                '  primary: "#533afd"\n')
        out, src = map_tokens(colors, self.text)
        self.assertEqual((out["--acc"], src), ("#533afd", "primary"))

    def test_low_contrast_primary_on_paper_takes_a_passing_color(self):
        colors = self.colors_of('  canvas: "#ffffff"\n  ink: "#111111"\n'
                                '  primary: "#ffe14d"\n'
                                '  brand-pale: "#ffd84a"\n'
                                '  accent-sky: "#0369a1"\n')
        out, src = map_tokens(colors, self.text)
        self.assertEqual((out["--acc"], src), ("#0369a1", "accent-sky"))

    def test_dark_paper_measures_against_paper(self):
        colors = self.colors_of('  canvas: "#0a0a0a"\n  ink: "#fafafa"\n'
                                '  primary: "#1e1b4b"\n  link: "#60a5fa"\n')
        out, src = map_tokens(colors, self.text)
        self.assertEqual((out["--acc"], src), ("#60a5fa", "link"))

    def test_fallback_accent_passes_near_black_and_near_white_paper(self):
        for paper in ("#000000", "#262626", "#f0f2f5", "#ffffff"):
            self.assertGreaterEqual(
                contrast(rgb(FALLBACK_ACCENT), rgb(paper)), 3, paper)

    def test_no_front_matter_is_none(self):
        self.assertIsNone(front_colors("# Brand\n\nprose only\n"))


CSS_COLOR = re.compile(r"^(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|color-mix\(.+\))$")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "jungle-deck-test"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


class GetdesignNetworkTest(unittest.TestCase):
    """SPEC "Verification plan": every getdesign file with front matter
    yields all mapped tokens or a derived value, and an accent != ink that
    reads on --paper. Prints the kept/swapped/fallback counts (#27)."""

    @unittest.skipUnless(os.environ.get("JD_NETWORK"), "set JD_NETWORK=1")
    def test_every_repo_file_maps(self):
        try:
            tree = json.loads(fetch(TREE))["tree"]
            paths = [t["path"] for t in tree if re.fullmatch(
                r"design-md/[^/]+/DESIGN\.md", t["path"])]
            with ThreadPoolExecutor(16) as pool:
                texts = list(pool.map(lambda p: fetch(RAW + p), paths))
        except (OSError, ValueError, KeyError) as e:  # offline, rate limit
            self.skipTest(f"GitHub not reachable: {e}")
        self.assertTrue(paths, "no DESIGN.md in the repo tree")
        doc = DESIGN.read_text(encoding="utf-8")
        kinds = {"kept": [], "swapped": [], "fallback": []}
        for path, text in zip(paths, texts):
            colors = front_colors(text)
            if colors is None:
                continue
            with self.subTest(path=path):
                out, src = map_tokens(colors, doc)
                kind = ("kept" if src == "primary"
                        else "fallback" if src is None else "swapped")
                kinds[kind].append(f"{path.split('/')[1]}:{src}")
                self.assertEqual(set(out), set(D25_CHAINS))
                for tok, value in out.items():
                    self.assertRegex(value, CSS_COLOR, tok)
                ink, acc = rgb(out["--ink"]), rgb(out["--acc"])
                paper = rgb(out["--paper"])
                self.assertIsNotNone(paper, "--paper not hex")
                self.assertIsNotNone(ink, "--ink not hex")
                self.assertNotEqual(acc, ink)
                # Only the fallback on a mid-tone paper may miss 3:1.
                if contrast(acc, paper) < 3:
                    self.assertEqual(out["--acc"], FALLBACK_ACCENT)
        self.assertTrue(any(kinds.values()), "no file with front matter")
        print()
        for kind, names in kinds.items():
            print(f"{kind} {len(names)}: {' '.join(names)}")


if __name__ == "__main__":
    unittest.main()
