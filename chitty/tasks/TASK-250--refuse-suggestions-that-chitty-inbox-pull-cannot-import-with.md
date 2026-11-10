---
title: Refuse suggestions that `chitty inbox --pull` cannot import, with a property test
status: todo
depends_on:
  - TASK-249
created: 2026-11-10
---

## Description

Second of two trial tickets for property tests.

**Property:** any suggestion that `inbox.suggest` accepts, `inbox.pull` imports, and the new ticket's title and Description equal what was sent. Normalise the Description as `pull` does: strip it, right-trim each line, and use `store.BACKLOG_DESCRIPTION` when it is empty.

**Fails today.** Each of these is accepted, then fails every later pull, because a pull is all or nothing:

- an empty title, a title containing U+2028, or one containing a C1 control such as `\x84`;
- a title ending in `---`: `_read_suggestion` splits the file on `---\n`, so pull raises `KeyError: 'created'`;
- a description with a text line followed by a `---` line (a setext heading).

**Fix:**

- `suggest` builds the ticket it would create with `model.new_task`, using the normalised Description, and raises that error as a `ChittyError` before writing anything. It still writes the text as given.
- `_read_suggestion` finds the frontmatter by its `---` delimiter lines, not by splitting on `---\n`.

Depends on TASK-249, whose re-parse check makes `new_task` reject `## Notes` lines, unclosed fences and form feeds in a Description. Those cases need it; the ones above do not.

**Test:** `tests/test_property_inbox.py`, inheriting `RepoTestCase`. One repository for the whole test, `project = "target"` in `chitty.toml` as `tests/test_inbox.py` does, `deadline=None`, about 50 examples. Draw Descriptions that include `## ` lines, fences and form feeds, which TASK-249 makes `new_task` reject. Count only `suggestion-*` files: `pull` also writes a registration file.

## Acceptance Criteria

- [ ] The property test fails before the fix, on the inputs above or others the generator finds, and passes after.
- [ ] `chitty suggest` with a U+2028 title, a title ending in `---`, or a setext-heading description exits non-zero and writes no suggestion file; a following `chitty inbox --pull` of another suggestion succeeds.

## Notes

Possible starting point: `refs/cold-read/TASK-250/2` (`git show refs/cold-read/TASK-250/2:<path>`). Check it against the criteria; don't trust it.

## History

- 2026-11-10T21:12:38Z jolly-heron → backlog
- 2026-11-10T21:17:27Z jolly-heron: replaced notes; changed description, acceptance criteria
- 2026-11-10T21:21:56Z jolly-heron: changed description, notes
- 2026-11-10T21:21:56Z jolly-heron backlog → todo
- 2026-11-10T21:58:53Z jolly-heron: replaced notes
