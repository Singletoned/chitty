---
title: Limit the word count of the guides in make check
status: done
created: 2026-11-16
---

## Description

The guides had grown to about 4,100 words by the 2026-11-16 retro. Put a word budget on each source so adding guidance requires either cutting something or explicitly increasing that file's budget.

Add `tests/test_guide_word_budget.py` with a module-level map of repository-relative paths to limits. Under `src/chitty/`, set `guide.md` to 75, `roles/cold-read.md` to 460, `roles/plan.md` to 1340, `roles/property-signals.md` to 180, `roles/rebase.md` to 75, `roles/repair.md` to 175, `roles/review.md` to 900, `roles/setup.md` to 570, and `roles/work.md` to 620. Count whitespace-separated words in raw UTF-8 Markdown using `len(text.split())`; exactly the limit passes. Do not change the guide text or the Makefile. Exclude other guide sources, including `src/chitty/guide-runner.md`.

Check the real tree rooted at the repository containing the test module, independent of the process working directory. Discover `src/chitty/guide.md` and every immediate `*.md` file under `src/chitty/roles/`; require the discovered set to match the map, so both a new file without a budget and a deleted file with a stale budget fail. Use the same assertion helper for real and temporary trees. For the temporary-tree tests, pass a small fixture-specific budget map and write actual files under a temporary root; do not modify repository guides or mock the filesystem. No property: use the standard library's word splitting directly, and test the fixed boundary and file-set failure modes.

## Acceptance Criteria

- [x] The discovered unittest passes on the current guides. In a temporary guide tree, a configured guide at exactly its limit passes, and adding one whitespace-separated word fails with its relative path, actual word count and limit.
- [x] In the same temporary tree, removing a budgeted role file or adding an unbudgeted role Markdown file fails and names the missing or unbudgeted path. The real-tree check runs under `make check`.

## Plan

Add a unittest module with a shared tree and word-budget assertion, exercise exact limits and file-set failures using real temporary files, and verify the repository guides through normal test discovery. Run formatting and the full checks before committing.

## Notes

Reviewed: The budgets, discovery scope and shared helper match the ticket; no property test is needed for standard word splitting.
1: pass - `make check` printed `Ran 974 tests` and `OK`. Running the temporary-tree test with `assertLessEqual` disabled printed `FAILED (failures=1)`, with `AssertionError not raised` at the over-limit assertion.
2: pass - `make check` discovered and passed the real-tree test. Running the temporary-tree test with set equality disabled printed `FAILED (errors=1)` on the missing role; ignoring extra files in set equality printed `FAILED (failures=1)` at the unbudgeted-file assertion.

## Summary

Added guide word budgets and shared assertions for real and temporary trees, including boundary and file-set failure checks. Verified with `make check` (974 tests), and ran `chitty fix` and `make format`. No follow-ups.

## History

- 2026-11-16T10:00:05Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:49Z intrepid-coral-raven backlog → planning
- 2026-11-21T15:49:40Z honest-coral-heron: changed description, acceptance criteria
- 2026-11-21T15:49:40Z honest-coral-heron planning → cold-read
- 2026-11-21T15:50:18Z honest-coral-heron cold-read → planning
- 2026-11-21T15:50:20Z honest-coral-heron planning → todo
- 2026-11-21T15:51:26Z witty-amber-jay todo → doing
- 2026-11-21T15:53:58Z witty-amber-jay: wrote the plan
- 2026-11-21T15:56:16Z witty-amber-jay: changed summary
- 2026-11-21T15:56:17Z witty-amber-jay doing → review
- 2026-11-21T16:00:28Z able-ochre-toad: changed notes; ticked acceptance criteria
- 2026-11-21T16:00:28Z able-ochre-toad review → done
