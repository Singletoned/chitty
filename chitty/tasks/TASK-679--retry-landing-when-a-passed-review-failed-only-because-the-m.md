---
title: Retry landing when a passed review failed only because the main checkout was dirty
status: backlog
created: 2026-11-24
---

## Description

In the echonomicon project (/Users/singletoned/src/singletoned/echonomicon), TASK-199 passed review on 2026-11-24 (review -> done at 12:25:09Z), then went done -> error 7 s later. The runner's landing step refused because the main checkout had an untracked file, tmp-plan-key-registry-check.log, left by a separate planning session. That file was later removed and the main checkout is now clean, but the ticket stays in error and the only routes back are re-reviewing it (setting it to review) or chitty run --errors, which starts an agent to repair something that needs no agent. Suggestions: (1) treat a dirty main checkout at landing as transient: leave the ticket in done-pending-land, or retry the land on the next loop iteration once git status is clean, instead of error; (2) or offer a deterministic 'chitty land TASK-N' that reruns only the rebase, check and fast-forward for a ticket whose latest review passed; (3) ignore untracked files that cannot conflict with the fast-forward, since git merge --ff-only only refuses on paths the merge would overwrite.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-24T22:21:41Z zesty-coral-newt → backlog
- 2026-11-24T22:21:43Z zesty-coral-newt: changed notes
