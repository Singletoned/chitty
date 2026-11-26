---
title: Find tickets changed on other branches in one pass per branch
status: backlog
depends_on:
  - TASK-598
created: 2026-11-23
---

## Description

Decided with the person, 2026-11-23: reads look at more than one branch, so a reader is told when its copy of a ticket is out of date (for example, done on another branch). This must not slow Chitty down, so the cross-branch facts are found once per command, per branch, never per ticket. It shares the per-command caching of `TASK-598`.

To be planned: a cached `Repo` index, built once per command and cleared in `_invalidate`, mapping each ticket ID to the branches that changed it since they split from `HEAD`. Candidate refs: on `main`, every local or remote-tracking branch (decided 2026-11-26: `main` gets the fullest view, see TASK-603); off `main`, the configured main branch and the ticket's own `task-<n>` branch. In both cases the current branch and any ref already contained in `HEAD` are skipped. One `git diff -z --no-renames --name-only HEAD...<ref> -- <ticket directories>` per remaining ref, skipping refs with unrelated histories. Measured 2026-11-23 in this repository: 17 such refs took 0.19 s in total, against 16 s for `chitty list`. Test: a counting wrapper (as in `TASK-598`) shows the number of Git calls depends on the number of refs, not tickets. Source selection should then use this index instead of its per-ticket `changed_since_split` and `is_ancestor` calls.

## History

- 2026-11-23T08:47:11Z plucky-umber-wren → backlog
- 2026-11-26T18:02:07Z brisk-bronze-adder: changed description
