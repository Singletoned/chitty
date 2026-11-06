---
title: Fail `make check` when a setup change has no version bump
status: doing
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Accepted by the human from the `TASK-108` retro, proposal 1. A missed or lost `__version__` bump caused failures on `TASK-93`, `TASK-104` and `TASK-126`, and two tickets bumping to the same version merge silently, so repositories never learn about the later change.

Add `scripts/check_version_bump.py`, using only Git and the standard library, as a step in `make check`:

1. If `refs/heads/main` does not exist, print a notice to stderr and pass. The release workflow checks out one commit of a tag with no `main`, and this is a guard on branches. On `main` itself, it passes too.
2. Decide what changed by comparing the working tree with the merge-base of `HEAD` and `main`, so a branch that is merely behind `main` is not blamed for files it did not touch. The watched files are `src/chitty/guide.md`, `src/chitty/integrations/pi/chitty.ts`, everything under `src/chitty/roles/`, and the text of the `INITIAL_CONFIG` string in `src/chitty/config.py`, found with a regular expression, rather than the whole of `config.py`, which changes for other reasons. A file added or removed counts as changed.
3. If any changed, `__version__` must be above the one in `main`'s tip, not the merge-base, so two tickets taking the same version are caught once the second is behind. Compare numerically, part by part. A version that is not dotted integers fails loudly.

Failure names the changed files and both versions.

## Acceptance Criteria

- [ ] Tests in temporary Git repositories show each watched change failing without a higher version and passing with one, the same version as `main`'s tip failing, `0.1.10` counting as above `0.1.9`, and an unrelated `config.py` change passing
- [x] Tests show a branch behind `main` that changed nothing passing, running on `main` passing, and a `--depth 1` clone at a tag with no `main` passing with a notice
- [x] `make check` runs it

## Plan

Implement a standard-library/Git-only version-bump guard script and invoke it from `make check`. Add temporary real-Git-repository tests covering watched-file changes, version comparisons, unrelated config changes, branch/main edge cases, and missing-main tags. Run the focused tests, then `make check` and tick only verified criteria.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: my criterion about the release workflow was false as written, because its checkout has no `main`; so a missing `main` passes with a notice. Comparing with `main`'s tip alone would blame a branch for files it never touched, so what changed comes from the merge-base and the version from the tip. Also the script's location, the template's extraction and `roles/`, which exists now. No `__version__` bump is needed: the script reaches no other repository.

Review failed (work): changing only the whitespace in the INITIAL_CONFIG assignment is an unrelated config.py change, but the guard compares the regex match including `INITIAL_CONFIG =` rather than only the string contents. A temporary Git repository with `INITIAL_CONFIG    = """initial"""` returns failure and demands a version bump; extract and compare the string text so formatting outside the string passes.

Review regression reproduced before fix: changing only whitespace around the INITIAL_CONFIG assignment was incorrectly treated as a setup change. The guard now compares only the string text, and the regression test passes.

## Summary

Implemented `scripts/check_version_bump.py` and added it to `make check`. The guard uses Git merge-base for changed setup files, compares the working-tree version to `main` tip, handles `main`/missing-main cases, and extracts only `INITIAL_CONFIG`. Added real temporary-Git tests for watched files, numeric versions, unrelated config changes, branch ancestry, and shallow tag clones. Verified with `make install`, focused tests, `chitty fix`, and `make check` (284 Python tests and Node tests pass). Follow-up: none.

## History

- 2026-11-04T20:45:25Z mellow-newt → backlog
- 2026-11-04T20:47:38Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:47:39Z mellow-newt backlog → todo
- 2026-11-05T22:22:37Z jolly-kestrel todo → doing
- 2026-11-05T22:22:58Z jolly-kestrel: wrote the plan
- 2026-11-05T22:50:48Z jolly-kestrel: ticked acceptance criteria
- 2026-11-05T22:50:49Z jolly-kestrel: ticked acceptance criteria
- 2026-11-05T22:50:50Z jolly-kestrel: ticked acceptance criteria
- 2026-11-05T22:50:55Z jolly-kestrel: changed summary
- 2026-11-05T22:50:55Z jolly-kestrel doing → review
- 2026-11-06T11:07:40Z eager-crane: changed acceptance criteria, notes
- 2026-11-06T11:07:40Z eager-crane review → doing
- 2026-11-06T14:56:57Z daring-adder: changed notes
