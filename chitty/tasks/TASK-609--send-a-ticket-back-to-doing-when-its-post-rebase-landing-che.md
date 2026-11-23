---
title: Send a ticket back to doing when its post-rebase landing checks fail
status: backlog
created: 2026-11-23
---

## Description

In taidy, TASK-10 passed review but `chitty run` landing (rebase onto `main`, then setup and checks) failed: the branch was 39 commits behind `main`, which had added a `ProcessingResult.unavailable` field and changed Prettier output, so two new tests broke after the rebase. Chitty moved the ticket review -> error, which stops the loop until a human intervenes, although this is an ordinary implementation defect against clear requirements that a worker could fix. Suggestion: when the rebase succeeds but the configured checks fail during landing, keep the rebased branch, write the check output to the note, and move the ticket to `doing` (or let the reviewer review the rebased branch before passing). Reserve `error` for runner failures such as an unresolvable rebase conflict. Related earlier suggestion: rebase an existing ticket branch onto `main` before the pre-work check.

## Notes

Suggestion origin: taidy

## History

- 2026-11-23T10:24:01Z witty-russet-gannet → backlog
- 2026-11-23T10:24:02Z witty-russet-gannet: changed notes
