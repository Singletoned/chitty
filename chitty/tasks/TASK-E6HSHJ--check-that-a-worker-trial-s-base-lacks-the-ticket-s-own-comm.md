---
title: Check that a worker trial's base lacks the ticket's own commits
status: backlog
created: 2026-11-25
provisional: true
---

## Description

This replaces `suggestion-d59cd03684994540af73a293c76261a7.md`, which has the same title and a description of only `-`. It was posted by mistake and can be deleted.

Evidence (2026-11-25, trial project `chitty-trial-claude-sonnet-task-664`): `TASK-664` was reset from `done` to `todo` for a worker trial, but its landed fix `b4441ac7` stayed on the trial's `main` and ticket branch, and both acceptance criteria stayed ticked. The worker could only confirm that nothing was left to build and set the ticket to `planning`, after running the tests with and without the fix and the full `make check` (about 6.5 minutes). The earlier worker and review notes, which describe the solution, were also still on the ticket.

Suggested: whatever prepares a trial should start from the commit before the ticket's first `Task: <ID>` code commit, or refuse when such a commit is in the base. It should also untick criteria and drop notes added by earlier runs.

## Notes

Suggestion origin: chitty-trial-claude-sonnet-task-664

## History

- 2026-11-25T22:28:46Z calm-ochre-quail → backlog
- 2026-11-25T22:28:48Z calm-ochre-quail: changed notes
