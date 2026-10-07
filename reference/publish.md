---
scope: The publish phase (SPEC D12, D13, D14, D17): commits, Pages copy, index card, push gate, live check, DESIGN.md feedback
authority: SPEC.md D12–D14. CLI lines here must match `scripts/publish.py --help`; tests/test_publish_reference.py checks them
status: draft 2026-10-07
---

# Publish phase

The `publish` phase puts one finished deck on the student's GitHub Pages
site. It starts when `BRIEF.md` has `phase: publish`. It ends when the live
deck matches the source, the index card is live, and `BRIEF.md` has
`phase: done`.

Read `jungle-deck.local.md` first (keys: `reference/local-template.md`).
Record each result in the `Publish` section of `BRIEF.md` when you get it.

## Rules

- Stage named files only. Never use `git add -A`, `git add .`, or
  `git commit -a`. A week repo holds other work that is not part of the deck.
- Never edit the Pages copy. Edit only the source deck in the week repo,
  then copy it again with `publish.py copy`. The copy is an output.
- Push only after an explicit yes from the student (step 5). Silence, a
  question, or "잠깐" is not a yes. Without a yes, do not push either repo.
- Ask for the push once. Do not ask again for each repo.
- Do not change the URL of a deck that is already published. Do not remove
  or rewrite an existing card.
- `scripts/publish.py` never runs git. You run git; the script copies and
  checks.

In the commands below, `<deck>` is the deck path from `BRIEF.md`
(`study/<deck-slug>/<deck-slug>.html`, relative to the week repo), `<N>` is
the week number, and `<deck-slug>` is `slug` from `BRIEF.md`. Run
`publish.py` from the skill directory, with `<deck>` as an absolute path.

## Steps

### 1. Commit in the week repo

1. Open `.gitignore` at the week repo root. Add each of these lines that is
   not there yet (D13):

   ```
   _backup/
   previews/
   .impeccable/
   ```

2. Stage the commit set by name: the deck HTML, `BRIEF.md`, the
   `evidence/` folder of this deck, and `.gitignore` if you changed it.

   ```
   git add .gitignore study/<deck-slug>/<deck-slug>.html study/<deck-slug>/BRIEF.md study/<deck-slug>/evidence/
   ```

3. Run `git status --short`. Make sure that nothing else is staged.
4. Commit. Record the commit hash in `BRIEF.md` (`Week repo commit`).

If `pages_repo` is empty, stop the Pages part here: print the absolute path
of the local deck HTML, do not copy, do not push, and do not make a card
(D15). Go to step 8, then step 9.

### 2. Copy the deck

```
python3 scripts/publish.py copy --deck <deck> --week <N>
```

The script copies the deck to `<pages_repo>/study/weekNN/<deck-slug>.html`
and compares the bytes. If it exits non-zero, show its message and stop.
Record the copy path in `BRIEF.md` (`Pages copy path`).

If the deck was published before, the copy replaces the old file at the
same URL. Do not change the slug.

### 3. Draft the index card

1. Make the deck URL: `<pages_url_base>study/weekNN/<deck-slug>.html`.
   Use the full absolute URL as the `href`. Do not use a relative href:
   `publish.py verify` searches the live index for the full absolute URL,
   so a relative href fails the check.
2. Fill the card format from `card_format` (`builtin`: see
   `reference/local-template.md`). Take the title, the description, and
   the meta line from `BRIEF.md`: the description comes from the
   Conclusion slot.
3. Search `<pages_repo>/index.html` for the deck URL. If a card already
   links it, keep that card and do not add a second one. If the old card
   has a relative href, change only that href to the absolute URL.
4. Show the drafted card to the student. Insert it into `index.html` in the
   group of that week. If no group matches, ask the student where to put
   it.

### 4. Commit in the Pages repo

Stage the copy and `index.html` by name. Commit in `pages_repo`. Record the
commit hash in `BRIEF.md` (`Pages repo commit`).

```
git -C <pages_repo> add study/weekNN/<deck-slug>.html index.html
```

### 5. Ask once

Show the student, in one message:

- the two commits (`git log -1 --stat` in each repo),
- the deck URL,
- the card text.

Ask one question: push both repos now? Push only after an explicit yes
("응", "yes", "push", "올려"). Record the answer in `BRIEF.md`
(`Push approved by student`). If the answer is not a yes, stop. Keep both
commits. Set `Next action` to "Ask the student to approve the push".

### 6. Push both repos

Push the week repo, then the Pages repo. If a push fails, show the error
and stop. Do not force-push.

### 7. Verify the live deck

```
python3 scripts/publish.py verify --deck <deck> --week <N>
```

The script polls the deck URL until it returns HTTP 200 and the live bytes
match the local deck. Then it searches the live index for the deck URL. A
Pages build takes 20–40 s, sometimes some minutes. The default timeout is
600 s; change it with `--timeout` only when the student asks.

- Exit 0: record the URL in `BRIEF.md` (`Live URL`, `Index card found`).
- Timeout on the deck: show the reason. Run `verify` again later. Do not
  push again.
- The live deck differs: fix the source deck, then go back to step 1. Do
  not edit the Pages copy.
- No card: check the href in `index.html` (step 3).

### 8. DESIGN.md

D14 and D17. Do this step also when `pages_repo` is empty.

If `design_md` is set:

1. Read the DESIGN.md at that path. It is in Google Labs DESIGN.md format:
   YAML token front matter, then the sections Overview, Colors, Typography,
   Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts.
2. Compare the deck with it. List each change that this deck made against
   DESIGN.md as one numbered diff item: the token or section, the old
   value, the new value. Example: `colors.accent: #d23c2c → #ff3300`.
3. Ask the student which items to apply. The student answers by number.
4. Apply only the items the student picks. Change nothing for the other
   items. If the student picks none, do not change DESIGN.md.
5. Record the applied item numbers in `BRIEF.md`
   (`DESIGN.md items applied`).

If `design_md` is empty:

1. Offer to extract a DESIGN.md from this deck, in Google Labs DESIGN.md
   format (the token front matter and the sections above).
2. If the student says yes, ask where to write it. Write it there. Record
   its path as `design_md` in `jungle-deck.local.md`. The next decks then
   skip style discovery (D17).
3. If the student says no, leave `design_md` empty.

Do not commit or push DESIGN.md unless the student asks.

### 9. Close the BRIEF

Only when the student confirms that the deck is live and done:

1. Set `phase: done` and `updated` in `BRIEF.md`.
2. Set `Next action` to "None. The deck is published."
3. Commit `BRIEF.md` alone in the week repo. Do not push it; it goes out
   with the student's next push.
