---
title: Failed chitty edit still leaves the ticket written but uncommitted
status: review
labels:
  - bug
  - escape
created: 2026-11-17
---

## Description

Seen 2026-11-17 in the `task-364` worktree: `chitty edit TASK-364 --note ...` failed with `TASK-356 is used by more than one file` (see `TASK-367`), but the note had already been written to the ticket file, which was left modified and uncommitted. `TASK-355` (done) was meant to stop a failed `chitty edit` leaving its write uncommitted; this failure happens in the lookup during finalize, which `TASK-355` apparently does not cover. Source ticket: `TASK-355`.

## Notes

Checked 2026-11-24 on `main` at `80f6f701`: does not reproduce. In an autocommit repository, in the main checkout and in a linked `task-1` worktree, `chitty edit TASK-1 --note hello` with a refusing `pre-commit` hook exits 1 and leaves `git status --porcelain` empty; with a second file for `TASK-2` committed, `chitty edit TASK-1 --note hello --depends-on TASK-2` succeeds and leaves the tree clean. `tests/test_failed_writes_restore.py` covers restoring after failed writes for every write command. Probably fixed after `TASK-355`; close it unless it is seen again.

## History

- 2026-11-17T20:00:43Z kind-umber-toad → backlog
- 2026-11-24T08:37:57Z kind-navy-toad: changed notes
- 2026-11-24T09:07:18Z kind-navy-toad backlog → review
