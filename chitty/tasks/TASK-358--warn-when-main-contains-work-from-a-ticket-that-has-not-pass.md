---
title: Warn when main contains work from a ticket that has not passed review
status: backlog
created: 2026-11-16
---

## Description

Seen 2026-11-16: `TASK-318` code reached `main` in `6a9e3ee` (Merge TASK-318 runner error fixes, 2026-11-13 19:37), 50 seconds after its worker moved it to review and before the review that then failed it. The managed `AGENTS.md` text tells agents started without `chitty run` to merge `main` into the branch, run checks, then fast-forward `main`, without saying the review must have passed first. Make `chitty check` on `main` warn about any commit reachable from `main` with a `Task: <ID>` trailer whose ticket is not `done`, and make the `AGENTS.md` text say landing needs a passing review.

## History

- 2026-11-16T10:29:29Z intrepid-coral-raven → backlog
