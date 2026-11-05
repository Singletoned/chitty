---
title: Pick the right copy of a ticket when commits share a second
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

Chitty picks the newest copy of a ticket across all refs by commit time, which has one-second precision. `_latest_changes` in `src/chitty/git.py` keeps the first commit it sees for a path unless a later one has a strictly greater timestamp, and `git log` does not promise that a child comes before a parent with the same timestamp. So a claim committed in the same second as the commit before it can lose to the older copy. `chitty run` then reports `TASK-1: doing → todo` and exits 0, although the session changed nothing, so an unattended loop carries on. It has not been seen outside tests here, because `make install` makes setup slow, but a quick `setup` hits it.

This is why `v0.1.27` and `v0.1.28` failed to publish: `test_run_refresh_is_silent_when_current_or_in_a_worktree` and `test_run_replaces_an_outdated_extension_before_starting_pi` fail on the GitHub runner, whose suite takes about 17 seconds against 118 locally. Setting `GIT_COMMITTER_DATE` and `GIT_AUTHOR_DATE` to one fixed time reproduces both locally.

Add `--topo-order` to the `git log` call in `_latest_changes`, so a child always comes before its ancestors. Tried on 2026-11-05 in a scratch clone: both tests then pass with the fixed dates and with the normal clock.

Out of scope: two unrelated branches changing one ticket in the same second, where neither copy is an ancestor and the choice stays arbitrary. No version bump is needed for this ticket: it changes nothing `chitty init` delivers.

## Acceptance Criteria

- [ ] A test with a child commit in the same second as its parent, using a fixed `GIT_COMMITTER_DATE`, shows `Repo.find` returning the child commit copy from both the branch worktree and the main checkout, and fails without the change

## History

- 2026-11-05T12:04:19Z mellow-newt → backlog
