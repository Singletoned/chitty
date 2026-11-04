---
title: Require a line per criterion in a review verdict
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Accepted by the human from the `TASK-108` retro, proposal 2. In 11 of 16 later-round failures, the finding was already visible at the previous review, including all 6 since `TASK-104` told reviewers to list every failure. A required form may work where a prompt did not. `TASK-167` changes the instructions; until then, the refusal message teaches the form.

A review verdict is `Repo.edit` in `src/chitty/store.py` moving a ticket from `review` to `done` or `doing` when its stored task has criteria. Split `note` and every entry of `notes` into lines, because the CLI and MCP pass them differently and one note may hold several lines. Each line matching `^(\d+): (pass|fail) - (\S.*)$` is a verdict line, in lowercase with an ASCII hyphen. There must be exactly one for each criterion number on the stored task, before this edit's other changes. Otherwise refuse, changing nothing, with a message showing the form and naming missing, duplicated or out-of-range numbers. `done` needs every line to be `pass`, and `doing` needs at least one `fail`. Other text is allowed, and `done` still needs its `Reviewed:` note.

Check this just after the existing `Reviewed:` check, before `_escalate_repeated_failure`, so a third failure also needs a valid verdict and the `blocked` ticket keeps it. `--override-review-independence` skips only the independence check, not this. A move to `blocked` and a ticket with no criteria are not affected, nor are contexts with `review = false`, which do not pass through `review`.

Existing tests that move a ticket with criteria out of `review` will need verdict lines. Tickets with no criteria need no change.

## Acceptance Criteria

- [ ] Tests through the CLI and MCP show a verdict refused for a missing line, a wrong word, a duplicate, an out-of-range number, `done` with a `fail` and `doing` with no `fail`, each changing nothing, and a complete verdict accepted for `done` and `doing`
- [ ] Tests show a third failure with a valid verdict still escalating to `blocked`, the override still needing the form, and a ticket with no criteria unaffected

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Too big as written, so the instructions moved to their own ticket. Fixed: the exact form, duplicates and out-of-range numbers, several notes, the `Reviewed:` prefix, escalation, and the override, which I decided should still need the form, because it answers who reviews, not what the verdict says.

Second cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: splitting notes into lines, which count of criteria, and where the check goes. Rejected: fixing the message's wording, which a test need only match on the numbers.

## History

- 2026-11-04T20:45:26Z mellow-newt → backlog
- 2026-11-04T20:47:40Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:48:49Z mellow-newt: changed description, notes
