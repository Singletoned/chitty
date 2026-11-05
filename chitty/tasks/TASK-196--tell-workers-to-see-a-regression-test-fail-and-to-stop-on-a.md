---
title: Tell workers to see a regression test fail, and to stop on a wrong ticket
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

Some faults only show up in the real implementation, however the ticket was read. On `TASK-31` in `echonomicon` a test passed with or without the fix, and on `TASK-137` here Luna left out a test, which `TASK-182` now adds. `src/chitty/roles/work.md` says nothing about either. The human agreed on 2026-11-05 to add this to the guide alongside implementing cold reads, which do not replace it.

Add this bullet to `src/chitty/roles/work.md`, adjusting only line wrapping:

"When a ticket asks for a regression test, see it fail without the fix, by running it before you write the fix or with the fix reverted, and say so in a note. If it passes without the fix, it proves nothing: change the test. If the ticket itself is wrong, because following it would break something or a claim in it is false, do not work around it: note what you found and set `-s blocked`. An unclear detail with a cheap default is not this: choose it, as below."

Put it before the bullet on cheap-to-reverse defaults, so that "as below" holds. This file ships to every repository, so do not name `make`. `chitty guide work` serves it at run time, and `AGENTS.md` does not hold it, so no `chitty init` or version bump is needed. Other tickets edit this file, including `TASK-173` and `TASK-179`, so add only this bullet.

Out of scope: having Chitty check that a test failed.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py`, collapsing whitespace in `guide("work")` first so that line wrapping cannot break it, shows it containing `see it fail without the fix`, `change the test`, `do not work around it` and `An unclear detail with a cheap default is not this`, and fails against the current `work.md`

## Notes

Implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-196/1`. Fixed: a test on exact phrases broke on line wrapping in my own wording; "change it" did not say what to change; when to run the test, and what happens on a ticket with no regression test; and the `TASK-137` claim, which that ticket's own text cannot confirm, now points at `TASK-182`. Checked: `TASK-173` and `TASK-179` do name `work.md`. Rejected: requiring a position or a bullet in the test, because the description says where it goes and the reviewer can read it.

## History

- 2026-11-05T17:53:54Z mellow-newt → backlog
- 2026-11-05T17:59:51Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T17:59:52Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T17:59:52Z mellow-newt backlog → todo
- 2026-11-05T18:13:37Z mellow-newt todo → backlog
