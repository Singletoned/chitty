---
title: Test the `configured main branch has no tip` error from `ticket_source`
status: backlog
created: 2026-11-21
---

## Description

Raised at `src/chitty/ticket_source.py` (about line 39) when a ticket has no ticket-branch candidate, the checkout is not on the configured main branch, and that branch has no commit, for example a repository on `master` with the default `main_branch`. `grep -rn "has no tip" tests` finds nothing. Found by the `TASK-378` cold read, 2026-11-21. Add a real-Git test through `Repo.source_copy` (in the style of `tests/test_source_copy_errors.py`) and one through `chitty show`.

## History

- 2026-11-21T09:12:33Z nimble-umber-gannet → backlog
