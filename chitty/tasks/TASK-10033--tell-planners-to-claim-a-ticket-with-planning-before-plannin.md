---
title: Tell planners to claim a ticket with `planning` before planning it on a branch
status: done
labels:
  - untestable
owner: human
depends_on:
  - TASK-10032
parent: TASK-10026
created: 2026-11-25
moved_from: TASK-WWNDDM
---

## Description

Part of `TASK-10026`, after `TASK-10032` makes `planning` a claim. Planners need to know to take the claim first, to work on a branch, and to leave other planners' tickets alone.

In `src/chitty/roles/plan.md`, replace the bullet that starts "Keep a new ticket in `backlog` until you work on it" with:

> - Take `to-plan` tickets before `backlog`. Claim one with `-s planning` in the main checkout, then plan it on a `plan/` branch, changing its text only when you have finished. Use `-s cold-read` for its cold read, `-s planning` again to settle findings, then `-s todo`, and land the branch. Leave a ticket another planner holds alone. Change status in the same edit as the text it depends on. Use `parent` to group flat IDs.

and, in the bullet that starts "Check tickets mentioned by `chitty edit -s todo`", replace "keep it in `planning` with a note" with "return it to `to-plan` with a note".

This replaces two sentences with about one more line; it removes "Keep a new ticket in `backlog` until you work on it", which the new first sentence covers.

## Notes

Review failed (work): The new bullet in `src/chitty/roles/plan.md` can be 12 words and 1 wrapped line shorter (5 lines instead of 6, matching the ticket's "about one more line") while keeping every requirement; the second edit ("return it to `to-plan` with a note") is fine. Use:

- Take `to-plan` tickets before `backlog`: claim one with `-s planning` in the
  main checkout, plan on a `plan/` branch, and edit its text only when finished.
  Use `-s cold-read`, `-s planning` to settle findings, then `-s todo` and land.
  Leave other planners' tickets alone. Change status in the same edit as the
  text it depends on. Use `parent` to group flat IDs.

Reviewed: diff of `main...task-10033` changes two bullets in `src/chitty/roles/plan.md`, using the 5-line wording from the previous review note and "return it to `to-plan` with a note". `TASK-10032` is `done`.
1: pass - the claim bullet says to take `to-plan` before `backlog`, claim with `-s planning` in the main checkout, plan on a `plan/` branch, edit text at the end, use `cold-read`/`planning`/`todo`, land, and leave other planners' tickets alone.
2: pass - the `chitty edit -s todo` bullet says "return it to `to-plan` with a note".

## Summary

Replaced the planning-claim bullet in `src/chitty/roles/plan.md` with the shorter 5-line wording from review (12 words and 1 wrapped line shorter):

- Take `to-plan` tickets before `backlog`: claim one with `-s planning` in the
  main checkout, plan on a `plan/` branch, and edit its text only when finished.
  Use `-s cold-read`, `-s planning` to settle findings, then `-s todo` and land.
  Leave other planners' tickets alone. Change status in the same edit as the
  text it depends on. Use `parent` to group flat IDs.

Kept the approved "return it to `to-plan` with a note" change in the `chitty edit -s todo` bullet.

Branch `task-10033` (worktree `.worktrees/task-10033`). `make check` passed via `chitty edit -s review`.

## History

- 2026-11-25T23:08:02Z golden-coral-stoat → backlog
- 2026-11-25T23:12:40Z golden-coral-stoat backlog → todo
- 2026-11-25T23:12:53Z golden-coral-stoat: renumbered from TASK-WWNDDM
- 2026-11-26T10:55:28Z tidy-silver-puffin todo → doing
- 2026-11-26T11:06:56Z tidy-silver-puffin: changed owner, summary
- 2026-11-26T11:06:56Z tidy-silver-puffin doing → review
- 2026-11-26T11:29:38Z human: changed owner, notes
- 2026-11-26T11:29:38Z human review → doing
- 2026-11-26T18:33:06Z calm-russet-badger: changed owner, summary
- 2026-11-26T18:33:06Z calm-russet-badger doing → review
- 2026-11-26T18:57:32Z intrepid-russet-falcon: changed notes
- 2026-11-26T18:57:32Z intrepid-russet-falcon review → done
