---
title: Pilot spec-first delivery on 3 to 5 tickets
status: backlog
priority: high
depends_on:
  - TASK-108
  - TASK-107
  - TASK-124
  - TASK-126
  - TASK-120
  - TASK-127
parent: TASK-106
created: 2026-11-03
---

## Description

Try the pipeline in `PLAN.md` ("Pipeline and feedback") by hand, on existing statuses, with no pipeline code, and use the result to decide which stages are worth building.

`TASK-107` must be done first, and `TASK-105` should be: Chitty runs from the ticket's worktree during the pilot, because running it from `main` forks a ticket that is on a branch.

Each pilot ticket gets the label `spec-first`, and a different session for every stage. Mapping onto today's statuses:

1. **Design** (`backlog`): written with the human to the ready definition. A fresh session then does the cold read, recorded with `--note`.
2. **Tests** (`backlog`): a fresh session writes failing tests from the ticket alone, on the ticket's branch, and notes the commit. The scripted check is that each test fails for the expected reason, not an import or setup error.
3. **Review-ticket** (`backlog` → `todo`): the human reads the ticket and tests together. Promotion to `todo` is the sign-off. A failure goes back with a note giving the cause.
4. **Work** (`todo` → `doing`): at most one ticket in `doing`, merged before the next starts. Before setting `review`, `git diff --exit-code <tests-commit> HEAD -- <test paths>` must pass and the tests must be green.
5. **Review-work** (`review`): a failure uses `Review failed (<cause>): ...`, its finding becomes a new criterion, and the next attempt is a fresh session. Stop for the human after the second failure on a ticket, ahead of the code's limit of three.

Sequence: use good models throughout on the first two tickets and label them `example`. Then use a cheap model for tests and work on the rest, to see what breaks. Candidates: `TASK-63`, `TASK-67`, `TASK-73`, `TASK-50`.

Decided with the human (2026-11-03): one ticket in work at a time. The human's available time is the limiting factor, so the pilot runs at the pace of review-ticket, with no deadline.

## Acceptance Criteria

- [ ] At least 3 tickets complete the full sequence, with at least one using a cheap model for tests and work
- [ ] Each pilot ticket records in `--summary` the model per stage, review rounds and failure causes, cold-read mismatches, predicted versus changed files, and approximate human time
- [ ] The report compares results with the `TASK-108` baseline, and gives a keep, change or drop decision for every stage, agreed with the human
- [ ] A retro is run on the pilot, including a check of what each spec test would have caught

## Notes

Model and cost per session now come from the `TASK-127` log, so the summary for each pilot ticket need only record the rest.

## History

- 2026-11-03T10:27:47Z lively-panda → backlog
- 2026-11-03T10:28:26Z lively-panda: changed dependencies, acceptance criteria
- 2026-11-03T10:41:01Z lively-panda: changed dependencies, description
- 2026-11-03T12:40:41Z lively-panda: changed dependencies
- 2026-11-03T16:30:18Z lively-panda: changed dependencies
- 2026-11-03T16:46:07Z lively-panda: changed dependencies, notes
