---
title: Ticket guard refuses when branch and main copies are identical
status: backlog
created: 2026-11-24
---

## Description

On 2026-11-23, `chitty list -s review -l untestable` on `main` failed with "Error: ticket `TASK-608` changed on both `task-608` and `main`". The `TASK-608` ticket file was byte-identical on both refs (`git diff main task-608 -- chitty/tasks/TASK-608*` was empty). The branch tip (f62f3ffd) was only a differently-dated rebase of the commit already on `main` (0ac614f7). The branch reflog shows the ref moved from 0ac614f7 to f62f3ffd with an empty reflog message, cause unknown (possibly another session). Resetting the branch to the landed commit cleared the error. Expected: identical copies should never be refused (compare with `TASK-385`, "Refuse a ticket write only when a newer, different copy exists elsewhere"), and a read-only `list` should not fail on a ticket it is not writing.

## Notes

Suggestion origin: chitty

Triage 2026-11-24, from TASK-681 (echonomicon): the same failure hit TASK-164. After the planner copied the archived file to `main`, every `chitty list` failed with "ticket `TASK-164` changed on both `task-164` and `main`" although both files were byte-identical. It cleared only after saving the branch head under `refs/superseded/task-164` and resetting the branch to `main`.

## History

- 2026-11-24T22:21:30Z zesty-coral-newt → backlog
- 2026-11-24T22:21:31Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:53Z zesty-coral-newt: changed notes
