---
scope: The setting of the weekly Krafton Jungle talk, the same for every student and every week (SPEC "Shared Jungle context", D22)
authority: SPEC.md "Shared Jungle context", D10, D22. tests/test_grill_reference.py checks the rows here
status: revised 2026-10-15; unverified draft (D19)
---

# Shared Jungle context

This is the setting of the weekly Krafton Jungle talk. It holds for every Jungle student, in every week: C weeks, Pintos weeks, and the later Python and AI weeks (D22).
Treat each row as a default, not as a question. Change a row only when the student says so.

Source: SPEC "Shared Jungle context", from the author's own words (sessions 2026-09-16 to 2026-10-15).

| Field | Value | Consequence for the presentation |
|---|---|---|
| Event | A weekly Thursday talk. The topic is what the student learned this week, in a refined, WIL-like form. | One presentation per week. The title slide states the point, lead-first (두괄식). |
| Audience | The cohort on the same week's curriculum. The level spread is wide. More than half already know the topic. | Do not explain the exercise. Lead with the surprise. Define this week's domain terms on screen (example: a project-specific macro or API name). |
| Language | Korean speech and prose. Code, identifiers, and tool output stay in their original form. | Use a font that renders Korean and code. Break Korean text at word boundaries. |
| Time | 2 minutes. No Q&A. The limit is background, not a gate (D10). | 6 ± 2 slides (a suggestion, not a rule). Do not run a timer check. Do not cut content only to fit the time. Speaker notes are a light suggested script unless the student confirmed a full script. |
| Display | A large monitor in a bright lecture room. | The accent, the code, and the logs must stay readable in bright light. Keep code text large. |
| Story type | Storytelling is preferred: "2분이지만 발표는 스토리텔링." A troubleshooting or experiment story fits best. | Use a narrative story frame (grill round 4), not an explanation-style list. |
| Evidence | Real output that the student ran this week: test results or terminal logs, from whatever toolchain the week uses. | Use only output the student ran. Each piece of evidence names the command that made it. |
| Reuse | The presentation also feeds the student's WIL. | Each slide must read without the speaker. Keep the notes in the file. |

## Not in this file

Speaker, publishing, and style settings are personal.
They live in `jungle-deck.local.md` in the skill directory (see `reference/local-template.md`).
Examples: the display name, the Pages repo and URL, the index card format, the DESIGN.md path, and the preferred accent.
