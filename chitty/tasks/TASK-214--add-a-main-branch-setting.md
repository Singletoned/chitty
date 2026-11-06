---
title: Add a `main_branch` setting
status: backlog
priority: medium
created: 2026-11-06
---

## Description

Chitty assumes the integration branch is called `main`. This ticket adds the setting; `TASK-215` uses it in the code, and `TASK-216` in the docs and guides.

Add `main_branch` to `RepoConfig` in `src/chitty/config.py`, for both `chitty.toml` and `[tool.chitty]`.

- **New repositories.** `chitty init` writes it from the current branch of the main checkout. If `HEAD` is detached, fail with an error that names `main_branch` and says to set it by hand. Outside Git, write nothing: non-Git use never needs a branch. In a linked worktree, `init` refuses (`TASK-212`).
- **Existing configs (migration rule).** A config without `main_branch` whose `chitty_version` is older than the version this change ships in means `"main"`, because that was the only behaviour then. Apply this when loading, before validation, so old configs keep working until they are upgraded. The upgrade (`init_repo`, and the autocommit upgrade in the main checkout) then writes the key, from the main checkout's current branch.
- **Missing key on a newer config.** A config at or after that version, inside Git, without the key fails to load. The error names `main_branch`.
- **Templates and test configs.** Add `main_branch` to `INITIAL_CONFIG` and to the test configs in `tests/support.py`, `tests/test_cli.py` and `tests/test_backlog_context.py`. Tests that run `init` in a fresh directory need `git init -b main` first, unless they test non-Git use.

This changes what `chitty init` writes, so bump `__version__` at patch level. Don't edit this repository's `chitty.toml` on the branch: the main checkout's upgrade adds the key after the work lands.

Out of scope: using the setting (`TASK-215`), docs (`TASK-216`), and remotes or `origin/HEAD`.

## Acceptance Criteria

- [ ] Tests show `chitty init` writing `main_branch = "master"` in a new repository on `master`, failing on a detached `HEAD` with an error naming `main_branch`, and writing no key outside Git.
- [ ] Tests show an old config without the key loading as `main` and gaining the key on upgrade, and a current-version config without it failing to load with an error naming `main_branch`.

## Notes

Cold read 1 (Sonnet, of the original whole-feature ticket; `make check` OK across about 15 files). Outcomes:
- Too large: fixed, split into this ticket (the setting), `TASK-215` (code) and `TASK-216` (docs and guides).
- A required key broke every existing config before `init` could add it: fixed with the migration rule above. An old config without the key means `main`, which isn't a hidden default because that was the only behaviour.
- Detached `HEAD`, linked worktree and non-Git `init`: decided above.
- Test-config churn: listed.
- The Pi extension doesn't mention `main`, and `chitty list` doesn't use `main_files`: those claims are gone from the split tickets.
- `_main_checkout` duplication: `TASK-215` reuses the existing one.
The ref `refs/cold-read/TASK-214/1` followed the old design and was deleted.

## History

- 2026-11-06T16:24:17Z youthful-toad → backlog
- 2026-11-06T16:48:05Z youthful-toad: changed title, description, acceptance criteria, notes
