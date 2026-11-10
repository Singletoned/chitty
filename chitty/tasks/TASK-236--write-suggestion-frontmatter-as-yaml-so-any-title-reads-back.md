---
title: Write suggestion frontmatter as YAML so any title reads back
status: backlog
priority: high
created: 2026-11-10
---

## Description

`suggest()` in `src/chitty/inbox.py` builds suggestion frontmatter with string formatting (`f"---\ntitle: {title}\n..."`). A title containing `: `, such as `Cold-read guide: suggest a stub-first red`, is then invalid YAML. `_read_suggestion` calls `yaml.safe_load` on it and the `ScannerError` escapes as a raw traceback, so `chitty inbox` and `chitty inbox --pull` fail for every waiting suggestion, not just the bad one.

Decisions:

- Write the frontmatter with `yaml.safe_dump` (keys `title`, `created`, `origin`, and `task` when given, in that order), so any title round-trips. Keep `created` an ISO date string.
- In `_read_suggestion`, catch `yaml.YAMLError` and raise `ChittyError` whose message names the suggestion file path, chained with `from` so the original error stays visible.

Out of scope: repairing malformed suggestion files that already exist; changing the inbox layout or `pull`.

Tests go in `tests/test_inbox.py` (`TestInbox` inherits `RepoTestCase`, so the inbox is a temporary one).

## Acceptance Criteria

- [ ] A test sends a suggestion titled `Guide: a title, with: colons and "quotes"` with `suggest()`, and `list_waiting` returns that exact title; the test fails before the fix.
- [ ] A test writes a waiting suggestion file whose frontmatter is invalid YAML; `list_waiting` raises `ChittyError` whose message contains the file path.

## History

- 2026-11-10T14:08:37Z jolly-heron → backlog
