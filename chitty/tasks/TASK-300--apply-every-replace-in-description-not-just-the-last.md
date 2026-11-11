---
title: Apply every `--replace-in-description`, not just the last
status: review
labels:
  - bug
parent: TASK-284
created: 2026-11-11
---

## Description

- `chitty edit` keeps only the last of several `--replace-in-description OLD NEW` options, silently (`src/chitty/cli.py:599`; `Edit.replace_in_description` in `src/chitty/store.py` holds one pair). The planner lost an edit this way on 2026-11-11.
- Make the option repeatable (`multiple=True`) and apply each pair in order, each to the result of the one before, with the existing checks (empty OLD, OLD not found, combined with `--description`) applied to every pair. The MCP `edit` tool (`src/chitty/mcp.py`) takes a list of pairs too; a single pair is no longer accepted there. The History line still says `changed description` once.

## Acceptance Criteria

- [x] A test: `chitty edit` with two `--replace-in-description` options changes both parts of the Description. It fails today.
- [x] If any OLD does not occur exactly once in the Description as the earlier pairs leave it, the edit fails naming that OLD and changes nothing. On "Keep a.", pairs (a→b, b→c) give "Keep c."; on "Keep a b.", the same pairs fail naming `b`.
- [x] MCP `edit` with two `replace_in_description` pairs changes both parts, and the History line for it reads `changed description`, not repeated.

## Plan

Update Edit to carry ordered replacement pairs; validate and apply each pair sequentially before writing so any failure leaves the task unchanged. Make the CLI option repeatable and accept a list of pairs through MCP. Add CLI and MCP regression coverage, including uniqueness after earlier replacements and one History action. Run the new regression tests against the current implementation first, then format and check.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-300/1`. Check it against the current criteria; do not trust it.

Regression test failed before the implementation: the CLI rejected a second replacement as having zero matches. Verified sequential matching and no-write-on-error behavior; MCP accepts multiple pairs and records one description history action. Full make format and make check passed.

## Summary

Implemented ordered, repeatable description replacement through CLI, store, and MCP. Verification: regression failed before the fix; make format and make check passed. No follow-up.

## History

- 2026-11-11T21:10:11Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:18Z vivid-yellow-raven: changed acceptance criteria
- 2026-11-11T21:10:22Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:16:06Z vivid-yellow-raven: changed description
- 2026-11-11T21:16:07Z vivid-yellow-raven: changed acceptance criteria, notes
- 2026-11-11T21:16:07Z vivid-yellow-raven cold-read → todo
- 2026-11-11T22:11:49Z open-dusky-dormouse todo → doing
- 2026-11-11T22:12:04Z open-dusky-dormouse: wrote the plan
- 2026-11-11T22:14:09Z open-dusky-dormouse: changed notes, summary; ticked acceptance criteria
- 2026-11-11T22:14:09Z open-dusky-dormouse doing → review
