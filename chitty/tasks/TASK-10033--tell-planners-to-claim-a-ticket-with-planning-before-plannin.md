---
title: Tell planners to claim a ticket with `planning` before planning it on a branch
status: doing
labels:
  - untestable
owner: untestable
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

## History

- 2026-11-25T23:08:02Z golden-coral-stoat → backlog
- 2026-11-25T23:12:40Z golden-coral-stoat backlog → todo
- 2026-11-25T23:12:53Z golden-coral-stoat: renumbered from TASK-WWNDDM
- 2026-11-26T10:55:28Z tidy-silver-puffin todo → doing
