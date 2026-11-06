---
title: Add a `main_branch` setting
status: backlog
priority: medium
created: 2026-11-06
---

## Description

Chitty assumes the integration branch is called `main`. This ticket adds the setting; `TASK-216` uses it in the code, and `TASK-217` in the docs and guides.

Add an optional `main_branch` to `RepoConfig` in `src/chitty/config.py`, for both `chitty.toml` and `[tool.chitty]`, defaulting to `"main"`. Settings are never required (the human's decision, 2026-11-06): a missing key means today's behaviour, so existing configs load unchanged and need no upgrade.

For a new repository, `chitty init` writes `main_branch` only when the current branch is something other than `main`, for example `master`. On `main`, a detached `HEAD` or outside Git, it writes nothing. Upgrades of existing configs never add it.

This changes what `chitty init` writes, so bump `__version__` at patch level. Don't edit this repository's `chitty.toml` on the branch.

Out of scope: using the setting (`TASK-216`), docs (`TASK-217`), and remotes or `origin/HEAD`.

## Acceptance Criteria

- [ ] Tests show a config without `main_branch` loading as `main`, and one with `main_branch = "master"` loading as `master`, from both `chitty.toml` and `[tool.chitty]`.
- [ ] Tests show `chitty init` writing `main_branch = "master"` in a new repository on `master`, and writing no `main_branch` on `main`, outside Git, or when upgrading an existing config.

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

## History

- 2026-11-06T16:24:17Z youthful-toad → backlog
- 2026-11-06T16:48:05Z youthful-toad: changed title, description, acceptance criteria, notes
- 2026-11-06T16:48:37Z youthful-toad: changed description
- 2026-11-06T16:48:42Z youthful-toad: changed notes
- 2026-11-06T16:49:06Z youthful-toad: changed description, acceptance criteria, notes
