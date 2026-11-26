---
title: Choose ticket sources with at most two Git calls per unmerged ticket branch
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

- `contains` stays a general two-argument function, because the mutant tests swap its arguments. Answer `contains(main_tip, tip)` from one `git for-each-ref --merged=<main_tip> --format=%(refname) refs/heads refs/remotes`, run at most once per `Repo` and cached until `_invalidate`. Other pairs still use `git.is_ancestor`.
- In `changed_on_both`, decide "the paths differ between the tips" in Python, by comparing the ticket's `(path, content)` pairs from `_ref_ticket_files` on `main` and on the ref (this needs no Git). Only when they differ, run `git diff --quiet <main_tip>...<tip> -- <paths>` and `git diff --quiet <tip>...<main_tip> -- <paths>` (each three-dot form diffs from the merge base). Keep the `refs <ref> and <main> have unrelated histories` error when there is no merge base.

Put the three-dot diff in `src/chitty/git.py` next to `changed_since_split`. Leave `changed_since_split` in place, because `_require_current_version` still uses it.

Out of scope: reading every non-ticket branch (TASK-603), and `src/chitty/run.py`.

## Acceptance Criteria

- [ ] A test in `tests/test_list_performance.py` counts Git calls under `GIT_TRACE` (as `_lookup_git_calls` does) for `chitty list` in a fixture with 1 and with 3 unmerged `task-<n>` branches, each committing a change to its own ticket. It asserts that count(3) - count(1) is at most 6 (3 per branch: `ls-tree` and two diffs), and it fails before the change
- [ ] Regression tests: `tests/test_ticket_placement_reads.py` (including its mutant tests), `tests/test_property_listing_conflicts.py`, `tests/test_source_copy_errors.py` and `tests/test_authoritative_listing.py`
- [ ] `make check` passes

## History

- 2026-11-23T08:47:11Z plucky-umber-wren → backlog
- 2026-11-26T18:02:07Z brisk-bronze-adder: changed description
- 2026-11-26T21:55:45Z youthful-lilac-heron backlog → planning
- 2026-11-26T21:57:53Z youthful-lilac-heron: changed title, priority, dependencies, description, acceptance criteria
- 2026-11-26T21:58:09Z youthful-lilac-heron planning → cold-read
