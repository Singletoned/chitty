---
title: Require a line per criterion in a review verdict
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Accepted by the human from the `TASK-108` retro, proposal 2. In 11 of 16 later-round failures, the finding was already visible at the previous review, including all 6 since `TASK-104` told reviewers in a prompt to report everything. A required form may work where the prompt did not. `TASK-46` also failed three times on one test that passed without the fix.

A review verdict is `chitty edit <ID>` moving a ticket out of `review` to `done` or `doing`, when the ticket has criteria. Its `--note` must hold one line per criterion: `<number>: pass - <evidence>` or `<number>: fail - <reason>`, where evidence is the command or test that shows it. Otherwise the write is refused, changing nothing, with a message showing the form and naming the missing numbers. `done` needs every line to be `pass`, and `doing` needs at least one `fail`. Other text in the note is allowed. Check this in `src/chitty/store.py`, so the CLI and MCP agree. `blocked` and a ticket with no criteria are not affected.

The review instructions say a test criterion passes only with evidence that the test fails without the change, and replace the "report everything" prompt rule with this form. The `TASK-109` pilot may later replace that test evidence.

## Acceptance Criteria

- [ ] Tests show a verdict refused with a missing line or a wrong word, and changing nothing, a complete verdict accepted for `done` and `doing`, and a ticket with no criteria unaffected
- [ ] The review instructions and `README.md` show the form, a test shows the instructions contain it, and `__version__` is bumped above `main`'s

## History

- 2026-11-04T20:45:26Z mellow-newt → backlog
