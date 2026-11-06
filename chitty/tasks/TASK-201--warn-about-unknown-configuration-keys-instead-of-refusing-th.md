---
title: Warn about unknown configuration keys instead of refusing them
status: backlog
priority: high
depends_on:
  - TASK-182
created: 2026-11-06
---

## Description

Today an unknown key in `chitty.toml` or `[tool.chitty]` fails every command with `Extra inputs are not permitted`, unless it is a top-level key and the file's `chitty_version` is newer than the running Chitty, in which case `_allow_newer_top_level_keys` in `src/chitty/config.py` drops it with a warning (`TASK-137`). On 2026-11-06 a branch adding `random_ids` under `[contexts.backlog]` made `main`'s `chitty run --mode review` refuse that branch's `chitty.toml`, so the review loop could not review it. The human decided on 2026-11-06 that an unknown key anywhere is a warning, never an error, whatever the version: only a few people use Chitty, and they will avoid typos.

Replace `_allow_newer_top_level_keys` with a function that removes every key `RepoConfig` does not define at the top level, and every key `ContextConfig` does not define inside each table under `contexts`, without reading `chitty_version`. It prints one line to stderr per file per process, as the existing `_WARNED_UNKNOWN_KEYS` set does, naming the keys with their full dotted path, for example `chitty.toml: ignoring unknown configuration key(s) colour, contexts.backlog.random_ids; check the spelling or upgrade Chitty`. Keys inside `[agent_commands]` are names the user chooses, so they are never unknown. Keep `extra="forbid"` on the models so that a key reaching validation is still a bug in this function rather than silently accepted. `UserContexts` and the inbox files are out of scope.

`TASK-182` is in review and changes the same function, so this ticket depends on it and starts from its result. The tests in `tests/test_config.py` that expect `Extra inputs` for an unknown key (around lines 88, 101 and 115) change to expect the warning and a loaded config; any other case there stays an error. This changes no guide or `chitty.toml` template, so no version bump is needed. Update `PLAN.md` and `README.md` where they describe unknown or newer keys.

## Acceptance Criteria

- [ ] Tests show an unknown top-level key and an unknown key in a `contexts` table, in both `chitty.toml` and `[tool.chitty]`, loading with one warning naming each dotted key, whatever `chitty_version` says
- [ ] `PLAN.md` and `README.md` describe the warning

## History

- 2026-11-06T09:26:16Z youthful-toad → backlog
