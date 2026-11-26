---
title: Choose ticket sources with three Git calls per unmerged ticket branch
status: cold-read
priority: high
depends_on:
  - TASK-SNYWDV
created: 2026-11-23
---

## Description

`Repo._choose_source` (`src/chitty/store.py`) passes `ticket_source` two callbacks, and each runs Git for every ticket branch it looks at:

- `contains(a, b)` runs `git merge-base --is-ancestor` on every call. Most calls are `contains(main_tip, tip)`, one for each `task-<n>` ref.
- `changed_on_both(name)` runs `git.paths_differ` and then two `git.changed_since_split` calls (a `merge-base` and a `diff` each): up to 5 calls.

On this repository on 2026-11-26 that came to about 80 of the 130 Git calls in `chitty list` (13 unmerged ticket branches, about 18 ms to start each Git process here).

Change, with `ticket_source` and its arguments unchanged:

- `contains` stays a general two-argument function, because the mutant tests swap its arguments. Answer `contains(main_tip, tip)` from the set of commit IDs printed by one `git for-each-ref --merged=<main_tip> --format=%(objectname) refs/heads refs/remotes`. Run it at most once per `Repo` and clear it in `_invalidate`. Other pairs still use `git.is_ancestor`.
- In `changed_on_both`, keep `git.paths_differ`, and replace each `git.changed_since_split` with a new `git.changed_since_split_point(root, ref, against, paths)` in `src/chitty/git.py`. It runs `git --literal-pathspecs diff --quiet <against>...<ref> -- <paths>`, which diffs from the merge base. It returns `False` without running Git when `paths` is empty, as `paths_differ` does. On exit 128, call `git.common_ancestor`: if that gives `None`, raise today's `refs <ref> and <against> have unrelated histories`; otherwise raise the diff's error.

Leave `changed_since_split` in place: `_require_current_version` still uses it.

Out of scope: reading every non-ticket branch (TASK-603), and `src/chitty/run.py`.

## Acceptance Criteria

- [ ] A test in `tests/test_list_performance.py` counts `trace: built-in: git` lines under `GIT_TRACE` for `chitty list` in a committed fixture (built like `TestScanCounts._fixture`) with 1 and with 3 unmerged `task-<n>` branches, each changing its own ticket only on the branch. It asserts that count(3) - count(1) equals 2 × a module constant `GIT_CALLS_PER_TICKET_BRANCH = 4` (`ls-tree`, `paths_differ` and two three-dot diffs), and it fails before the change
- [ ] A test in `tests/test_git.py` asserts that the new three-dot helper raises `ChittyError` matching `unrelated histories` for two commits with no common ancestor, and returns `False` for an empty path list. Regression tests: `tests/test_ticket_placement_reads.py` (including its mutant tests), `tests/test_property_listing_conflicts.py`, `tests/test_source_copy_errors.py` and `tests/test_authoritative_listing.py`
- [ ] `make check` passes

## History

- 2026-11-23T08:47:11Z plucky-umber-wren → backlog
- 2026-11-26T18:02:07Z brisk-bronze-adder: changed description
- 2026-11-26T21:55:45Z youthful-lilac-heron backlog → planning
- 2026-11-26T21:57:53Z youthful-lilac-heron: changed title, priority, dependencies, description, acceptance criteria
- 2026-11-26T21:58:09Z youthful-lilac-heron planning → cold-read
- 2026-11-26T22:00:42Z youthful-lilac-heron: changed title, description, acceptance criteria
