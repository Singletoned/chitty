---
title: Write suggestion frontmatter as YAML so any title reads back
status: doing
priority: high
created: 2026-11-10
---

## Description

`suggest()` in `src/chitty/inbox.py` builds suggestion frontmatter with string formatting (`f"---\ntitle: {title}\n..."`). A title containing `: `, such as `Cold-read guide: suggest a stub-first red`, is then invalid YAML. `_read_suggestion` calls `yaml.safe_load` on it and the `ScannerError` escapes as a raw traceback, so `chitty inbox` and `chitty inbox --pull` fail for every waiting suggestion, not just the bad one.

Decisions:

- Write the frontmatter with `yaml.safe_dump(..., sort_keys=False, allow_unicode=True)` (keys `title`, `created`, `origin`, and `task` when given, in that order), so any single-line title round-trips and non-ASCII stays readable. Keep `created` an ISO date string.
- `suggest()` rejects a title containing a newline with `ChittyError`; titles are one line.
- In `_read_suggestion`, when the `---` delimiters are missing or `yaml.YAMLError` is raised, raise `ChittyError` whose message names the suggestion file path, chained with `from` so the original error stays visible. Keep the existing message, `<path>: invalid suggestion frontmatter`. Update `test_pull_releases_invalid_suggestion_and_restores_config`, which writes a file without delimiters and currently expects `ValueError`.

Out of scope: repairing malformed suggestion files that already exist; changing the inbox layout or `pull`.

Tests go in `tests/test_inbox.py` (`TestInbox` inherits `RepoTestCase`, so the inbox is a temporary one).

## Acceptance Criteria

- [ ] A test sends a suggestion titled `Guide: a title, with: colons and "quotes"` with `suggest()`, and `list_waiting` returns that exact title; the test fails before the fix.
- [ ] Tests write waiting suggestion files with invalid-YAML frontmatter and with no `---` delimiters; `list_waiting` raises `ChittyError` whose message contains the file path for each.
- [ ] `suggest()` with a title containing a newline raises `ChittyError` and writes no file.

## Notes

Cold read 1 (Haiku): fixed: a title holding a `---` line broke the delimiter split, so `suggest()` now rejects newlines in titles. Fixed: `allow_unicode=True`. Fixed: missing delimiters raised a raw `ValueError`; now the same `ChittyError`, and the existing pull test is updated. Verified: `created` reads back unchanged; `pull`/`claim` need no change. Possible starting point: `git diff main...refs/cold-read/TASK-236/1`; check it against the current criteria, not trust it.

## History

- 2026-11-10T14:08:37Z jolly-heron → backlog
- 2026-11-10T14:18:07Z jolly-heron: changed description, acceptance criteria, notes
- 2026-11-10T14:18:53Z jolly-heron backlog → todo
- 2026-11-10T16:48:24Z youthful-zander todo → doing
