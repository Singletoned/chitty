---
title: Route missing review branches to error repair
status: planning
parent: TASK-318
created: 2026-11-13
---

## Description

When review finds that the ticket branch and its worktree are missing, transition the ticket to `error`, not `blocked`, and record the missing branch and review context in the error note. An explicit `chitty run --errors` must select it for repair: the repair agent can recover the original branch and return it to `review`, or set it to `blocked` when human help is needed. The repair agent may recover a known original implementation commit from Git objects, reflogs or other locally available evidence; it must record the commit ID and evidence before returning to `review`. If no original commit can be identified, it must set the ticket to `blocked` with an explanation. Do not automatically recreate the missing ticket branch from `main` and present it as recovered work. Preserve unrelated unsafe-failure reporting. Update `tests/test_review_merge.py` and the relevant runner guidance. Use real temporary repositories and fake agents; no real model session. A missing branch and its Git worktree require real Git operations, so a pure function cannot test the recovery boundary. Write the regression first and record its pre-fix failure.

## Acceptance Criteria

- [ ] A review with no ticket branch or worktree changes the ticket to `error`, records the missing branch and review context, and is not selected by ordinary work or review; the regression fails before the change.
- [ ] An explicit fake-agent repair restores a known original implementation commit and records its ID and evidence before returning to `review`; if the original commit cannot be identified, it sets the ticket to `blocked`. The runner does not automatically recreate the missing ticket branch from `main` as though it were restored.

## History

- 2026-11-13T23:27:55Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:26Z mellow-umber-lapwing: changed title, description
- 2026-11-14T09:23:16Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-14T09:23:16Z mellow-umber-lapwing backlog → planning
- 2026-11-14T09:23:19Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:23:19Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:27:58Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-14T09:27:58Z mellow-umber-lapwing cold-read → planning
- 2026-11-14T09:28:01Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:32:06Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:32:06Z mellow-umber-lapwing cold-read → planning
