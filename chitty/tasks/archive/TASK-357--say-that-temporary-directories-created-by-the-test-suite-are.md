---
title: Say that temporary directories created by the test suite are allowed
status: done
labels:
  - untestable
owner: untestable
created: 2026-11-16
---

## Description

Seen 2026-11-16 on `TASK-321`: the review guide says to read and change only files inside the worktree, including scratch files. A reviewer took that to forbid the test suite using the system temp dir, set `TMPDIR` inside the worktree, which nested test repositories inside the git worktree and produced 46 failures, then failed the review as `integration`. In `src/chitty/roles/review.md` and `work.md`, make the rule cover files the agent creates, and say that temporary directories the repository tests create for themselves are fine. Revisit when agents run in containers.

## Notes

Stopgap until agents run in containers (`docs/plan/direction.md`, 2026-11-16): keep the wording change to one sentence, since the sandbox will replace the rule.

Implemented directly by the planning session as an untestable guide change, commit 3c23ca6.

Reviewed: untestable wording change, read by the planning session; make check passes.

## History

- 2026-11-16T10:29:27Z intrepid-coral-raven → backlog
- 2026-11-16T10:37:05Z intrepid-coral-raven: changed notes
- 2026-11-16T10:38:58Z intrepid-coral-raven backlog → planning
- 2026-11-16T16:48:16Z open-russet-eel: changed labels, owner
- 2026-11-16T16:48:31Z open-russet-eel planning → todo
- 2026-11-17T18:29:04Z kind-umber-toad: changed notes
- 2026-11-17T18:29:04Z kind-umber-toad todo → review
- 2026-11-17T18:29:06Z kind-umber-toad: changed notes; overrode review independence
- 2026-11-17T18:29:06Z kind-umber-toad review → done
- 2026-11-17T18:29:08Z kind-umber-toad done → archived
