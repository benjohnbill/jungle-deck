---
scope: The design phase (SPEC D17, D25): style source, previews, accent, getdesign.md mapping, the Design section of BRIEF.md
authority: SPEC.md D14, D17, D25, "Template tokens". tests/test_design_reference.py checks the rules here; its network test applies the mapping table below to every getdesign.md file
status: new 2026-10-15; unverified draft (D19)
---

# Design phase

The `design` phase fixes the style of the presentation (D17).
It starts when `BRIEF.md` has `phase: design`.
It ends when the `Design` section of `BRIEF.md` is filled and the student confirms it.

Read these first:

1. `BRIEF.md`. The `Grill` section tells you the topic and the mood.
2. `jungle-deck.local.md` (keys: `reference/local-template.md`). You need `design_md` and `accent`.
3. `reference/context.md`. The room is bright; the accent and the code must stay readable there.

## Steps

1. **`design_md` is set.** Ask "이번에도 이 스타일로 갈까요?".
   Yes: map that DESIGN.md with "Token mapping" below, confirm the accent (step 4, accent only), and go to step 5.
   No: go to step 2.
2. **Ask for a reference.** Ask both questions in one message:
   "원하는 디자인 레퍼런스가 있어요? (사이트 URL, 이미지, DESIGN.md)" and
   "getdesign.md 레퍼런스 중에서 고를까요?".
   A reference leads to step 3.1. A yes to getdesign.md leads to step 3.2. No to both leads to step 3.3 or 3.4.
   When the reference is the student's own DESIGN.md, write its path to `design_md` in local.md.
   When `design_md` is missing from local.md (not empty) and the student has no DESIGN.md, write `design_md: ""` (D16).
3. **Pick the style source.** Use the first source that applies. Use one source only.
   1. The student's reference.
      A DESIGN.md: map it with "Token mapping".
      A site URL or an image: read its colors and fonts, then fill the same six tokens and the fonts by hand.
   2. A getdesign.md pick. Follow "getdesign.md references".
   3. `frontend-slides` style discovery, when that skill is installed: run its style discovery (mood, previews, pick).
   4. The vendored presets: `vendor/frontend-slides/STYLE_PRESETS.md`. Propose two or three presets that fit a bright room and code on screen, and recommend one.
4. **Previews, then the accent.**
   1. Write two or three previews to `<save folder>/previews/<name>.html`. Each is a copy of `templates/stage.html` with only the `:root` tokens changed.
   2. Give the student the paths. The student picks one.
   3. Propose the accent: `accent` from local.md when it is set, else two or three candidates from the picked source. Recommend one. The student confirms.
   4. When `accent` is missing from local.md (not empty), ask "이 강조색을 다음 발표에도 쓸까요?". Write the accent on yes, `""` on no (D16).
5. **Record and confirm.** Fill the `Design` section of `BRIEF.md` (see "The Design section"). Ask "이 디자인으로 발표 자료를 만들까요?". Set `phase: build` only after the student says yes.

A dark canvas (a dark `--paper`): say once that the room is bright and a dark page washes out there. If the student keeps it, use it.

## getdesign.md references

getdesign.md is the site of the VoltAgent `awesome-design-md` repo (MIT). Its files use the Google DESIGN.md format: YAML front matter with `colors:` and `typography:`, then prose.

**Say this first, every time you propose a getdesign.md reference:**
"getdesign.md 레퍼런스에서는 색과 글꼴 분위기만 가져와요. 슬라이드 전체 스타일이 필요하면 frontend-slides 프리셋을 보세요."

1. **List the brands** from the raw README, with no `npx`:
   `https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/README.md`.
   Each brand is a link `https://getdesign.md/<brand>/design-md` with a one-line mood.
2. **Recommend two or three brands** whose mood fits the topic from `Grill`. Link each preview: `https://getdesign.md/<brand>/design-md`.
3. **Fetch the pick**: `https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/design-md/<brand>/DESIGN.md`.
   The README can miss a brand that the repo has; fetch a named brand directly before you call it missing.
   A 404 means the brand is not in the repo: the student downloads it from getdesign.md and gives you the path.
4. **A file with no front matter** (no `---` on line 1) is not recommended. If the student picks one anyway, treat it as the student's own reference (step 3.1): read its prose by hand.
5. Map the file with "Token mapping".

## Token mapping

Map a DESIGN.md (the student's, or a getdesign.md file) into the `:root` of `templates/stage.html`.
Set only these six tokens and the fonts. The template derives the other colors from `--acc`, `--ink`, and `--paper` with `color-mix()`.

For each token, read the `colors:` keys in order. The first key that is present wins.

| Token | `colors:` keys, first present wins |
|---|---|
| `--paper` | `canvas` |
| `--ink` | `ink` |
| `--acc` | `primary` |
| `--mut` | `ink-mute`, `ink-muted`, `muted`, `mute`, `ink-subtle`, `body` |
| `--panel` | `canvas-soft`, `surface-soft`, `surface-1`, `surface` |
| `--grid` | `hairline`, `hairline-soft` |

**Empty chain** (no key present):

- `--mut`: `color-mix(in srgb, var(--ink) 60%, var(--paper))`
- `--panel`: `color-mix(in srgb, var(--ink) 4%, var(--paper))`
- `--grid`: `color-mix(in srgb, var(--ink) 12%, var(--paper))`
- `--paper`, `--ink`: keep the template value. These are the base of every `color-mix()`; tell the student which one fell back.
- `--acc`: apply the accent rule.

**Accent rule.** The accent sits on the page. Measure it against the mapped `--paper` value (`paper`). The accent fails when `primary` is missing, equals `ink`, or has a contrast below 3:1 against `paper` (WCAG contrast ratio). Then:

1. Search the colors in this order: `link`, `link-*`, `brand-*`, `accent*`, then every other color in file order. Take the first color that passes all three tests: saturated (HSL saturation 0.4 or more, lightness 0.2 to 0.8), not equal to `ink`, and a contrast of 3:1 or more against `paper`.
2. No color passes: use `#3b82f6`. This mid blue keeps 3:1 against a near-black and a near-white paper. On a mid-tone paper, `#3b82f6` can also fall below 3:1 (`nintendo-2001`). Tell the student when you show it.
3. Ask the student to confirm the accent. Show the color you took and the key it came from.

**Fonts.** Take the font family only, from the body and display entries of `typography:`.
Append a Korean font to each stack (`'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif`). A paid or proprietary family (for example `sohne-var`) falls back to a system font in the browser: say so to the student in one line.
Keep the template's `clamp()` sizes. Take only `fontWeight`, `letterSpacing`, and `lineHeight`.

**Only the color and type mood transfer.** Components, spacing scales, radii, shadows, gradients, and decorative signatures stay in the source file.

## The Design section

Write these three lines in the `Design` section of `BRIEF.md`. `build` reads the style only from here (D9).

- `Source`: the student's DESIGN.md path, the reference URL or image, `getdesign.md/<brand>`, the frontend-slides pick, or the vendored preset name. `publish` branches on this value (D14).
- `Tokens`: the six token values and the two font stacks, as written to `:root`. Mark each fallback (template value or `color-mix()`).
- `Accent`: the confirmed accent and where it came from.
