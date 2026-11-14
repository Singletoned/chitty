---
title: Route missing review branches to error repair
status: cold-read
owner: planning
parent: TASK-318
created: 2026-11-13
---

## Description

When review finds that the ticket branch and its worktree are missing, transition the ticket to `error`, not `blocked`, and record the missing branch and review context in the error note. An explicit `chitty run --errors` must select it for repair: the repair agent can recover the original branch and return it to `review`, or set it to `blocked` when human help is needed. Never silently treat a newly created empty branch as the recovered implementation. Preserve unrelated unsafe-failure reporting. Update `tests/test_review_merge.py` and the relevant runner guidance. Use real temporary repositories and fake agents; no real model session. A missing branch and its Git worktree require real Git operations, so a pure function cannot test the recovery boundary. Write the regression first and record its pre-fix failure.

## Acceptance Criteria

- [ ] A review with no ticket branch or worktree changes the ticket to `error`, records the missing branch and review context, and is not selected by ordinary work or review; the regression fails before the change.
- [ ] An explicit fake-agent repair can restore the original branch and return the ticket to `review`, or mark it `blocked` when it cannot; a fresh empty branch is not silently accepted as restored. Tests exercise both outcomes and preserve existing branches and worktrees.

## History

- 2026-11-13T23:27:55Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:26Z mellow-umber-lapwing: changed title, description
- 2026-11-14T09:23:16Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-14T09:23:16Z mellow-umber-lapwing backlog → planning
- 2026-11-14T09:23:19Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:23:19Z mellow-umber-lapwing planning → cold-read
