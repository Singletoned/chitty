---
title: Repair agent cannot edit a ticket from its worktree when the run recorded branch main
status: backlog
created: 2026-11-21
---

## Description

In echonomicon on 2026-11-19, `chitty run --loop --errors` (chitty 0.6.1, pi print mode, gpt-6-luna) sent TASK-156 to a repair agent in `.worktrees/task-156`, on branch `task-156`. The agent reported: "Chitty task record says its branch is `main`, while the preserved worktree is on `task-156`. Chitty refuses task edits from that worktree and directs them to the main checkout." So it could not set `review` or `blocked`, the ticket stayed in `error`, and the loop exited 1 with "repair agent left TASK-156 in invalid status error". The repair prompt says to commit task changes in the ticket worktree, which contradicts that refusal. Either record the ticket branch correctly when the work run starts, or let the repair agent change status from the worktree, or tell it in the prompt where status edits must go. The earlier suggestion about not halting the loop on an invalid repair status also applies here.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-21T07:57:54Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:56Z nimble-umber-gannet: changed notes
