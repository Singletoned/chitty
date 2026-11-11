---
title: "Watch: cold reads need a base ref and pruning of stale reads"
status: backlog
priority: low
owner: human
created: 2026-11-10
---

## Description

Waiting to see whether this happens again. Do not implement yet; when it recurs, add a note with where and how, then decide.

First seen in the mullion planning session (2026-11-09):

- Cold-reading a ticket whose dependencies have not landed needed a base built from their reads. The planner built it by hand with `git merge-tree --write-tree` and `commit-tree`, once with a temporary `GIT_INDEX_FILE`. Proposed: `chitty guide cold-read <ID> --base <ref>`, defaulting to the latest read of each unlanded dependency.
- Refs from reads of superseded ticket text were tracked by hand and swept at the end. Proposed: record the ticket text hash a read used, and a `chitty cold-read prune` that keeps the latest per ticket.

## History

- 2026-11-10T14:08:44Z jolly-heron → backlog
