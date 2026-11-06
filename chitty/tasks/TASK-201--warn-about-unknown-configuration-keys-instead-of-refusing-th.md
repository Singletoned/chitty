---
title: Warn about unknown configuration keys instead of refusing them
status: done
priority: high
depends_on:
  - TASK-182
created: 2026-11-06
---

## Description

Today an unknown key in `chitty.toml` or `[tool.chitty]` fails every command with `Extra inputs are not permitted`, unless it is a top-level key and the file's `chitty_version` is newer than the running Chitty, in which case `_allow_newer_top_level_keys` in `src/chitty/config.py` drops it with a warning (`TASK-137`). On 2026-11-06 a branch adding `random_ids` under `[contexts.backlog]` made `main`'s `chitty run --mode review` refuse that branch's `chitty.toml`, so the review loop could not review it. The human decided on 2026-11-06 that an unknown key anywhere is a warning, never an error, whatever the version: only a few people use Chitty, and they will avoid typos.

Replace `_allow_newer_top_level_keys` with a function that removes every key `RepoConfig` does not define at the top level, and every key `ContextConfig` does not define inside each table under `contexts`, without reading `chitty_version`. Keys are paths within the Chitty table, so `[tool.chitty]` reports `contexts.backlog.random_ids`, not `tool.chitty.…`. It prints one line to stderr per file per process, keeping the existing `_WARNED_UNKNOWN_KEYS` set keyed by path, listing top-level keys sorted and then context keys sorted, for example `chitty.toml: ignoring unknown configuration key(s) colour, contexts.backlog.random_ids; check the spelling or upgrade Chitty` (the source path as `load_repo_config` has it). Keys inside `[agent_commands]` are names the user chooses, so they are never unknown. A `contexts` value, or a context, that is not a table is left for validation to reject as today. Keep `extra="forbid"` on the models so a key reaching validation is still a bug in this function rather than silently accepted. `UserContexts` and the inbox files are out of scope.

`TASK-182` is in review and changes the same function, so this ticket depends on it and starts from its result. In `tests/test_config.py` (names as on `task-182`), these change to expect the warning and a loaded config, and may be merged where they become duplicates: `test_newer_config_ignores_unknown_top_level_keys_once`, `test_equal_version_refuses_unknown_top_level_keys`, `test_unknown_top_level_keys_refuse_without_a_newer_version`, `test_unknown_context_keys_still_refuse_in_newer_config`, and `test_prerelease_version_loads_without_unknown_top_level_keys`'s unknown-key case, which no longer parses the version. Remove the `"Extra inputs"` entry from `test_rejections`; every other rejection there stays an error. `chitty init` reads the raw file in `_add_missing_settings`, so it must keep an unknown key and still succeed.

This changes no guide or `chitty.toml` template, so no version bump is needed. Add a sentence on unknown keys to the repository configuration section of `PLAN.md` and to the configuration paragraph of `README.md` (neither describes them today).

## Acceptance Criteria

- [x] Tests show an unknown top-level key and an unknown key in a `contexts` table, in both `chitty.toml` and `[tool.chitty]`, loading with one warning naming each dotted key, whatever `chitty_version` says
- [x] `PLAN.md` and `README.md` describe the warning
- [x] Tests show `[agent_commands]` entries with any name accepted without a warning, a non-table `contexts` value still refused, and `chitty init` on a file with an unknown key succeeding and keeping the key

## Plan

Inspect the configuration models and existing unknown-key tests, then add a sanitizer that warns once per source path while removing unknown top-level and context-table keys before validation. Preserve validation for malformed contexts and dynamic agent command names, update regression tests and documentation, run the required regression test before the fix where applicable, then run format and full checks.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-06. Fixed: one line per file listing every key, key order, key paths within the Chitty table for `pyproject.toml`, non-table contexts left to validation, every test that changes named (including `test_rejections` and the prerelease case), `chitty init` with an unknown key, and that the docs gain a sentence rather than update one; added a third criterion for those cases. Rejected: changing the per-path dedupe, because a second, different set of unknown keys in one file within one process cannot happen when the file is read once per command.

Regression test failed before the sanitizer with Extra inputs for unknown context keys. Verified the focused configuration and init tests, ruff, pyright, and the full Python test suite through the existing run-worktree test hang; make check and npm test timed out in that pre-existing hang after their completed checks.

Reviewed: implementation, tests, and documentation independently; focused configuration and init tests pass (28 tests), format, ruff, and pyright pass. make check reached the Python suite, which timed out in the existing run-worktree cleanup hang after completed checks.

1: pass - configuration warnings and filtering verified
2: pass - PLAN.md and README.md updated
3: pass - agent commands, malformed contexts, and init preservation verified

## Summary

Implemented recursive unknown-key filtering for repository configuration. Unknown top-level and context keys now warn once per source path with dotted paths and are removed before strict validation; dynamic agent command names and malformed contexts retain validation. Added coverage for both config sources, all version states, init preservation, and docs. Focused tests, ruff, and pyright pass; full check is blocked by an existing test-suite hang in run-worktree cleanup.

## History

- 2026-11-06T09:26:16Z youthful-toad → backlog
- 2026-11-06T09:31:12Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T09:31:15Z youthful-toad backlog → todo
- 2026-11-06T18:48:40Z nimble-eel todo → doing
- 2026-11-06T18:48:51Z nimble-eel: wrote the plan
- 2026-11-06T19:17:27Z nimble-eel: changed notes, summary; ticked acceptance criteria
- 2026-11-06T19:17:27Z nimble-eel doing → review
- 2026-11-06T19:21:22Z honest-lapwing: changed notes; ticked acceptance criteria
- 2026-11-06T19:21:22Z honest-lapwing review → done
