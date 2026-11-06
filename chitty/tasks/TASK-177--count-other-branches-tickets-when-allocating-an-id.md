---
title: Count other branches' tickets when allocating an ID
status: done
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

Parallel ticket branches hand out the same IDs, and the clash only shows up when they merge. `Repo.next_number` in `src/chitty/store.py` returns the highest number among task files in the current checkout plus one, so it never sees tickets committed on other branches. In `echonomicon` on 2026-11-04, review follow-ups filed from separate worktrees collided: `TASK-24` was created on three branches within six minutes, and `TASK-25` to `TASK-27` the same way. After merging, `chitty check` fails, `Task: <ID>` trailers and notes become ambiguous, `chitty show` can display the wrong ticket, and `chitty next` can name an ambiguous ID.

Have `next_number` also count every ticket file in this context, active and archived, from `self._history()`, which already reads the newest committed files from all local and remote-tracking branches. `_history` holds the whole `chitty/` tree, so filter on the file's parent being the context's directory or its archive directory. Read filenames only, with `ids.parse_filename`, skipping `IdError`, and do not parse the contents: a bad file on another branch must not stop `add`. `move` uses the same function, so it gains this too.

This does not cover uncommitted tickets in another worktree, which is what `autocommit = false` leaves, or unpushed work on another machine. Both are accepted. `historical_files` also returns nothing on a Git error, until `TASK-164` lands, and allocation then falls back to this checkout alone. `PLAN.md` currently says `max(n over existing files)` and that collisions are assumed not to happen, so correct both passages.

Split on 2026-11-05: repairing a collision that has already happened, and giving tickets raised on branches their own IDs, are separate tickets.

## Acceptance Criteria

- [x] A test with a ticket committed only on another branch, with no worktree, shows `chitty add` on `main` taking the number above it, in both active and archived locations, and fails without the change
- [x] `PLAN.md`'s ID rule and its passage on collisions say allocation counts committed tickets on all local and remote-tracking branches, active and archived, and does not see uncommitted tickets in other worktrees or unpushed work on other machines

## Plan

Inspect Repo.next_number and history helpers, add a filename-only scan of committed active and archive task paths from _history, and cover active/archive branch-only allocation with regression tests. Update PLAN.md ID and collision rules to document branch visibility limits. Run the full check suite, then record verified criteria and handoff.

## Notes

Suggestion origin: echonomicon

Cold read by a fresh Sonnet subagent, 2026-11-05. It reproduced the bug in a scratch repository: with tickets 2 and 3 only on another branch, `chitty add` on `main` gave `TASK-2`, so the criterion cannot pass with nothing built. Fixed: `PLAN.md` contradicting this; filtering `_history`; and not parsing contents, because `_tasks_in_location` raises on a bad file on any branch. Rejected: staleness, because the CLI and MCP open a new `Repo` per call, and renamed files, which only over-count.

Reviewed: independently inspected the implementation, regression test, and PLAN.md; targeted branch-only active/archive allocation test passes, and make check passed ruff, pyright, and 269 unittest tests. Both acceptance criteria are met.

## Summary

Implemented branch-aware ID allocation in Repo.next_number by scanning committed filenames from local and remote-tracking history across active and archive directories, while ignoring malformed filenames and file contents. Added a regression test covering active and archived tickets committed on a branch whose worktree is removed, and updated PLAN.md with visibility and collision rules. Verified with targeted regression, make check (ruff, pyright, 269 unittest tests passed); npm test emitted 26 dots but did not finish within the command timeout.

## History

- 2026-11-05T09:16:09Z upbeat-quail → backlog
- 2026-11-05T09:16:10Z upbeat-quail: changed notes
- 2026-11-05T14:43:39Z mellow-newt: changed title, priority, parent, description, acceptance criteria
- 2026-11-05T14:46:34Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:46:35Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:46:36Z mellow-newt backlog → todo
- 2026-11-05T20:48:07Z lively-vole todo → doing
- 2026-11-05T20:48:20Z lively-vole: wrote the plan
- 2026-11-05T20:56:25Z lively-vole: ticked acceptance criteria
- 2026-11-05T20:56:26Z lively-vole: ticked acceptance criteria
- 2026-11-05T20:56:36Z lively-vole: changed summary
- 2026-11-05T20:56:36Z lively-vole doing → review
- 2026-11-05T20:59:43Z daring-heron: changed notes
- 2026-11-05T20:59:43Z daring-heron review → done
