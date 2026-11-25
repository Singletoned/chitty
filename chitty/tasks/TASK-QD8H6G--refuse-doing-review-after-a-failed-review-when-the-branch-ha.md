---
title: Refuse `doing -> review` after a failed review when the branch has no new code commit
status: backlog
priority: medium
created: 2026-11-25
provisional: true
---

## Description

Evidence: echonomicon TASK-217, 2026-11-24. Review failed (work) asking to restore three deleted tests and fix a fake. The next worker set the summary to "Restored registry tests and corrected fake conditional-write semantics. mate check passes" and moved to `review`, but made no code commit: `git log main..task-217` shows no commit after the review, the tests are still deleted and the fake unchanged. A second reviewer had to rediscover both findings.

Suggestion: on `doing -> review` after a failed review, have chitty (or the runner) refuse or warn when the branch has no non-chitty commit since the review-failed transition. This is deterministic and would catch false "fixed" claims cheaply.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-25T22:28:50Z calm-ochre-quail → backlog
- 2026-11-25T22:28:51Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:32Z calm-ochre-quail: changed title, priority
