---
title: Pick the right copy of a ticket when commits share a second
status: doing
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

Chitty picks the newest copy of a ticket across all refs by commit time, which has one-second precision. `_latest_changes` in `src/chitty/git.py` keeps the first commit it sees for a path unless a later one has a strictly greater timestamp, and `git log` does not promise that a child comes before a parent with the same timestamp. So when the older commit is the tip of a ref that sorts before the child's ref, as `main` does before `task-1`, and both share a second, the older copy wins. A claim committed in the same second as `main`'s tip does this. `chitty run` then reports `TASK-1: doing → todo` and exits 0, although the session changed nothing, so an unattended loop carries on. It has not been seen outside tests here, because `make install` makes setup slow, but a quick `setup` hits it.

This is why `v0.1.27` and `v0.1.28` failed to publish: `test_run_refresh_is_silent_when_current_or_in_a_worktree` and `test_run_replaces_an_outdated_extension_before_starting_pi` fail on the GitHub runner, whose suite takes about 17 seconds against 118 locally. Setting `GIT_COMMITTER_DATE` and `GIT_AUTHOR_DATE` to one fixed time reproduces both locally.

Add `--topo-order` to the `git log` call in `_latest_changes`, so a child always comes before its ancestors, and leave `src/chitty/store.py` alone. It costs nothing measurable: 0.30s with or without it on this repository's 975 commits. Tried on 2026-11-05 in a scratch clone: both tests then pass with the fixed dates and with the normal clock.

Out of scope: two unrelated branches changing one ticket in the same second, where neither copy is an ancestor and the choice stays arbitrary. No version bump is needed for this ticket: it changes nothing `chitty init` delivers.

## Acceptance Criteria

- [x] A test with a parent at the tip of `main` and its child on a branch named `task-1`, in one second using a fixed `GIT_COMMITTER_DATE`, and a clean main checkout, shows `Repo.find` returning the child's copy from both the branch worktree and the main checkout. The note says it was run without the change and failed

## Plan

1. Add --topo-order to the git log invocation used by _latest_changes.
2. Add or update a regression test that creates main and task-1 commits at the same fixed second and verifies Repo.find selects the child from both checkouts.
3. Run the focused test, then make check and chitty fix; record verification and move the ticket to review.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: the serious one, that the criterion could pass with nothing built, because a child normally already comes first and a branch sorting before `main` would never lose, so it now names `main` and `task-1`; I ran this rather than assuming it. Also fixed: the stated cause, leaving `store.py` alone, and the cost. Filed separately: a conflict-resolved merge possibly dropping a ticket. No version bump: confirmed.

Moved to `doing` by the planning session so it runs next: the release is waiting on it.

Regression test failed before the fix (status was todo instead of doing) with main and task-1 commits sharing the fixed second; it passes after adding --topo-order. Module-by-module unittest runs, ruff, pyright, and npm test pass. Full unittest discovery did not complete within 600 seconds despite individual modules passing.

## History

- 2026-11-05T12:04:19Z mellow-newt → backlog
- 2026-11-05T12:06:13Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T12:06:14Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T12:06:15Z mellow-newt backlog → todo
- 2026-11-05T12:06:31Z mellow-newt: changed notes
- 2026-11-05T12:06:31Z mellow-newt todo → doing
- 2026-11-05T12:13:40Z eager-kestrel: wrote the plan
- 2026-11-05T13:12:58Z eager-kestrel: changed notes
- 2026-11-05T13:28:54Z eager-kestrel: ticked acceptance criteria
