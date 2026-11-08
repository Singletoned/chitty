---
title: Note a successful cold read on the ticket as help for the worker
status: backlog
created: 2026-11-06
---

## Description

When an implementing cold read against the current ticket text succeeds (its fail-first tests fail on the main branch and pass after its change, and it has no unresolved serious findings), the planning guide should tell the planner to add a ticket note pointing at the kept ref (`refs/cold-read/<ID>/<n>`), with the diff command, as a possible starting point for the worker, and a reminder to check it against the criteria rather than trust it.

The guide should also say to delete refs from reads made against superseded ticket text (`git update-ref -d refs/cold-read/<ID>/<n>`). The note gives `git diff <main-branch>...refs/cold-read/<ID>/<n>` with `<main-branch>` being the repository’s configured main branch. The proposed warning on notes added by non-claimants to `doing` or `done` tickets is out of scope for this guide-only change. Their tests pass, so a worker could trust them and copy behaviour the ticket has since changed.

Seen in echonomicon: `TASK-56` had three reads. The first two implemented a rule that a later finding replaced ("no word starts before the cut" became "no word ends before it"). Only the third matched the final ticket, and nothing on the ticket said which one to use.

A related gap: a planner can add notes after another session has already claimed or finished a ticket. In echonomicon, a note offering the worker a starting point landed on `TASK-56` after it was merged, and `TASK-57` had moved to a worktree in `doing`. It might help if `chitty edit --note` warned when the ticket is `doing` or `done` and the actor is not its claimant.

## Acceptance Criteria

- [ ] A fail-first guide test verifies `chitty guide plan` tells planners to note a successful ref from a read of the current ticket with no serious findings, include a diff against the configured main branch, warn the worker to check the current criteria, and delete superseded refs; `make check` passes.

## Notes

Suggestion origin: echonomicon

Cold-read finding: define a successful ref as one implemented against the current ticket text with no unresolved serious findings. The non-claimant `doing`/`done` note warning is a separate feature and out of scope. Require a guide regression test that fails before the fix. Clarify the diff command uses the configured main branch.

Resolved the cold-read ambiguity in the description; the guide handoff is only for a successful read against the current ticket and the stale-note warning is out of scope.

## History

- 2026-11-06T13:58:02Z youthful-toad → backlog
- 2026-11-06T13:58:03Z youthful-toad: changed notes
- 2026-11-08T14:15:13Z eager-puffin: changed notes
- 2026-11-08T14:15:30Z eager-puffin: changed description
- 2026-11-08T14:15:32Z eager-puffin: changed description
- 2026-11-08T14:15:34Z eager-puffin: changed acceptance criteria, notes
