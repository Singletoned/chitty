---
title: Refuse suggestions that `chitty inbox --pull` cannot import, with a property test
status: backlog
depends_on:
  - TASK-249
created: 2026-11-10
---

## Description

Second of two trial tickets for property tests.

**Property:** any suggestion that `inbox.suggest` accepts, `inbox.pull` imports, and the new ticket's title and Description equal what was sent (Description as Chitty normalises it).

**Fails today.** Each of these is accepted, then fails the whole pull, because a pull is all or nothing:

- a title containing U+2028 (`frontmatter keys must be plain 'key: value'`)
- a description with a text line followed by a `---` line (`setext headings are not allowed`)
- a description with `## Acceptance Criteria` then `1. [ ] x`

**Fix:** `suggest` builds the ticket it would create with `model.new_task`, and raises that error as a `ChittyError` before writing anything.

**Test:** `tests/test_property_inbox.py`, inheriting `RepoTestCase` so the inbox is temporary. Use one repository for the whole test, `deadline=None`, and about 50 examples, since each pull commits.

## Acceptance Criteria

- [ ] The property test fails before the fix with one of the three inputs above, and passes after.
- [ ] `chitty suggest` with each of the three inputs exits non-zero and writes no suggestion file; a following `chitty inbox --pull` of another suggestion succeeds.

## History

- 2026-11-10T21:12:38Z jolly-heron → backlog
