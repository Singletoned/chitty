---
title: Require a line per criterion in a review verdict
status: done
priority: medium
created: 2026-11-04
---

## Description

Accepted by the human from the `TASK-108` retro, proposal 2. In 11 of 16 later-round failures, the finding was already visible at the previous review, including all 6 since `TASK-104` told reviewers to list every failure. A required form may work where a prompt did not. `TASK-167` changes the instructions; until then, the refusal message teaches the form.

A review verdict is `Repo.edit` in `src/chitty/store.py` moving a ticket from `review` to `done` or `doing` when its stored task has criteria. Split `note` and every entry of `notes` into lines, because the CLI and MCP pass them differently and one note may hold several lines. Each line matching `^(\d+): (pass|fail) - (\S.*)$` is a verdict line, in lowercase with an ASCII hyphen. There must be exactly one for each criterion number on the stored task, before this edit's other changes. Otherwise refuse, changing nothing, with a message showing the form and naming missing, duplicated or out-of-range numbers. `done` needs every line to be `pass`, and `doing` needs at least one `fail`. Other text is allowed, and `done` still needs its `Reviewed:` note.

Check this just after the existing `Reviewed:` check, before `_escalate_repeated_failure`, so a third failure also needs a valid verdict and the `blocked` ticket keeps it. `--override-review-independence` skips only the independence check, not this. A move to `blocked` and a ticket with no criteria are not affected, nor are contexts with `review = false`, which do not pass through `review`.

Existing tests that move a ticket with criteria out of `review` will need verdict lines. Tickets with no criteria need no change.

## Acceptance Criteria

- [x] Tests through the CLI and MCP show a verdict refused for a missing line, a wrong word, a duplicate, an out-of-range number, `done` with a `fail` and `doing` with no `fail`, each changing nothing, and a complete verdict accepted for `done` and `doing`
- [x] Tests show a third failure with a valid verdict still escalating to `blocked`, the override still needing the form, and a ticket with no criteria unaffected

## Plan

Add shared review-verdict validation in store.py immediately after the existing Reviewed: check. Split note and notes into lines, require exactly one lowercase pass/fail verdict for every stored criterion, reject malformed/missing/duplicate/out-of-range verdicts without mutation, and enforce status-specific pass/fail rules. Add CLI and MCP regression coverage including escalation, override, and no-criteria cases; update existing review-transition fixtures as needed.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Too big as written, so the instructions moved to their own ticket. Fixed: the exact form, duplicates and out-of-range numbers, several notes, the `Reviewed:` prefix, escalation, and the override, which I decided should still need the form, because it answers who reviews, not what the verdict says.

Second cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: splitting notes into lines, which count of criteria, and where the check goes. Rejected: fixing the message's wording, which a test need only match on the numbers.

Reviewed: criteria and implementation independently; make check passed (306 unittest tests and Node tests).
1: pass - CLI and MCP coverage verifies refusal, no mutation, and complete done/doing verdicts.
2: pass - escalation, override, and no-criteria behavior are covered and verified.

## Summary

Implemented shared review-verdict validation in store.py. CLI and MCP tests cover malformed, missing, duplicate, out-of-range, status-specific, complete, override, escalation, and no-criteria cases. make check passes: ruff, pyright, 280 unittest tests, and Node tests. Commit 595b53d (Task: TASK-166).

## History

- 2026-11-04T20:45:26Z mellow-newt → backlog
- 2026-11-04T20:47:40Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:48:49Z mellow-newt: changed description, notes
- 2026-11-04T20:48:50Z mellow-newt backlog → todo
- 2026-11-05T22:51:12Z daring-eel todo → doing
- 2026-11-05T22:51:31Z daring-eel: wrote the plan
- 2026-11-05T22:59:54Z daring-eel: ticked acceptance criteria
- 2026-11-05T22:59:55Z daring-eel: ticked acceptance criteria
- 2026-11-05T23:00:01Z daring-eel: changed summary
- 2026-11-05T23:00:01Z daring-eel doing → review
- 2026-11-06T11:15:54Z able-zander: changed notes
- 2026-11-06T11:15:54Z able-zander review → done
- 2026-11-11T10:17:37Z vivid-yellowhammer: changed parent
