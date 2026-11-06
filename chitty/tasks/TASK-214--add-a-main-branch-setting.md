---
title: Add a `main_branch` setting
status: review
priority: medium
created: 2026-11-06
---

## Description

Chitty assumes the integration branch is called `main`. This ticket adds the setting; `TASK-216` uses it in the code, and `TASK-217` in the docs and guides.

Add an optional `main_branch` to `RepoConfig` in `src/chitty/config.py`, for both `chitty.toml` and `[tool.chitty]`, defaulting to `"main"`. Settings are never required (the human's decision, 2026-11-06): a missing key means today's behaviour, so existing configs load unchanged and need no upgrade.

For a new repository, `chitty init` writes `main_branch` only when the current branch is something other than `main`, for example `master`. Get the branch from the existing `git.current_branch`, which returns `None` outside Git or on a detached `HEAD`. Insert the line after formatting `INITIAL_CONFIG`, quoted with `json.dumps`, rather than adding a placeholder that would leave a blank line. A `[tool.chitty]` config that already exists is an upgrade, so it gets no key. On `main`, a detached `HEAD` or outside Git, it writes nothing. Upgrades of existing configs never add it.

No `__version__` bump: no existing repository gains anything by re-running `init`, and `scripts/check_version_bump.py` only requires one when `INITIAL_CONFIG` changes. Don't edit this repository's `chitty.toml` on the branch.

Out of scope: using the setting (`TASK-216`), docs (`TASK-217`), and remotes or `origin/HEAD`.

## Acceptance Criteria

- [x] Tests show a config without `main_branch` loading as `main`, and one with `main_branch = "master"` loading as `master`, from both `chitty.toml` and `[tool.chitty]`.
- [x] Tests show `chitty init` writing `main_branch = "master"` in a new repository on `master`, and writing no `main_branch` on `main`, outside Git, or when upgrading an existing config.

## Plan

1. Inspect config parsing, git.current_branch, init templates, and existing tests.
2. Add optional RepoConfig.main_branch with a main default and add focused config/init tests, first confirming the new regression test fails before the implementation.
3. Run formatting and the full check suite, then verify both acceptance criteria and prepare the ticket for review.

## Notes

Cold read 1 (Sonnet, of the original whole-feature ticket; `make check` OK across about 15 files). Outcomes:
- Too large: fixed, split into this ticket (the setting), `TASK-215` (code) and `TASK-216` (docs and guides).
- A required key broke every existing config before `init` could add it: fixed with the migration rule above. An old config without the key means `main`, which isn't a hidden default because that was the only behaviour.
- Detached `HEAD`, linked worktree and non-Git `init`: decided above.
- Test-config churn: listed.
- The Pi extension doesn't mention `main`, and `chitty list` doesn't use `main_files`: those claims are gone from the split tickets.
- `_main_checkout` duplication: `TASK-215` reuses the existing one.
The ref `refs/cold-read/TASK-214/1` followed the old design and was deleted.

Split note correction: the code ticket is `TASK-216` and the docs ticket `TASK-217`; `TASK-215` is unrelated.

Rescoped on 2026-11-06. The human said "The easy solution is don't have required settings", so `main_branch` is optional with default `main`. The migration rule and the missing-key error are gone. The second cold read was stopped before it reported.

Cold read 2 (Sonnet, `refs/cold-read/TASK-214/1`; the `master` tests failed before and passed after; `make check` OK). Outcomes:
- The version bump would make every repository warn for no benefit: fixed, no bump.
- How `init` knows the branch: fixed, the ticket points to `git.current_branch`.
- An optional line in `INITIAL_CONFIG`: fixed, insert after formatting.
- An existing `[tool.chitty]` is treated as an upgrade: stated.
- The reader added a non-empty validator: accepted.
- The detached-`HEAD` and outside-Git tests pass both before and after: accepted, because they test that nothing is written.
The ref includes a version bump, so a worker should drop that hunk.

Regression tests failed before implementation: RepoConfig had no main_branch and init omitted the master setting. After implementation, config loading and init coverage pass for chitty.toml, [tool.chitty], main, detached/outside Git, and existing-config upgrades. chitty fix emitted pre-existing Markdown delimiter warnings for unrelated tickets but made no changes.

## Summary

Implemented optional RepoConfig.main_branch with a default of "main". New init configs record a non-main current branch using JSON quoting; main, detached/outside-Git, and existing configs remain unchanged. Added config and init regression coverage. Verified with make format && make check (351 Python tests and Node tests pass). Commit: 211c171.

## History

- 2026-11-06T16:24:17Z youthful-toad → backlog
- 2026-11-06T16:48:05Z youthful-toad: changed title, description, acceptance criteria, notes
- 2026-11-06T16:48:37Z youthful-toad: changed description
- 2026-11-06T16:48:42Z youthful-toad: changed notes
- 2026-11-06T16:49:06Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T16:59:24Z youthful-toad: changed description, notes
- 2026-11-06T16:59:24Z youthful-toad backlog → todo
- 2026-11-06T20:42:03Z lively-yellowhammer todo → doing
- 2026-11-06T20:43:21Z vivid-urchin: wrote the plan
- 2026-11-06T20:47:26Z vivid-urchin: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:47:26Z vivid-urchin doing → review
