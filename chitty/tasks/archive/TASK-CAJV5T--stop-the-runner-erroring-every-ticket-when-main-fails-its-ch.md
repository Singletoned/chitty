---
title: Stop the runner erroring every ticket when main fails its check
status: backlog
created: 2026-11-26
provisional: true
---

## Description

Evidence (echonomicon, 2026-11-25 23:49 to 2026-11-26 00:01): four tickets in a row (TASK-238, TASK-244, TASK-BCHE6A, then TASK-226 at review) went to `error` with "Runner error (check): check exited with status 2 ... the branch has no work yet, so `main` fails this check". The runner already knew `main` was failing, yet picked up and errored each next ticket. The cause was one flaky test on `main` (a Hypothesis deadline exceeded under the load of parallel checks), so every error was the same and unrelated to its ticket. Cleaning up meant rebasing four branches and resetting four statuses by hand.

Suggestions:
1. When the check fails on a branch with no work, treat it as "main is broken": stop picking new tickets (or pause the loop), report once, and leave the ticket in its previous status instead of `error`.
2. Before recording a check failure as an error, re-run just the failing check once; if it passes the second time, record it as flaky (with the log) rather than erroring the ticket.
3. Optionally, `chitty run --errors` could detect a batch of errors with the same check-log failure and offer to reset them together after `main` is fixed.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-26T10:54:57Z calm-ochre-quail → backlog
- 2026-11-26T10:54:59Z calm-ochre-quail: changed notes
- 2026-11-26T10:56:41Z calm-ochre-quail backlog → archived
