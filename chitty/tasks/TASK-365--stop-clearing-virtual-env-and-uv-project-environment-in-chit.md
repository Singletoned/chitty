---
title: Stop clearing `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` in `chitty run`
status: planning
created: 2026-11-17
---

## Description

`TASK-238` made `chitty run` remove `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` from the environment of the agent and of the setup, check and landing-check commands, because one person's shell exported them pointing at a shared environment. That shell has since been fixed, and the human decided (`HUMAN-10`, 2026-11-17) that no other users should hit it. Remove the code.

- In `_command_environment` in `src/chitty/run.py` (or `command_environment` in `src/chitty/commands.py` if `TASK-343` has landed), delete the two `pop` calls for `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` and the comment that explains them. Keep the `CHITTY_USAGE_FILE` removal.
- Delete the tests that assert the two variables are removed: the three tests in `tests/test_run_environment.py`, and the parts of `test_run_uses_runner_chitty_and_strips_worktree_environment` in `tests/test_next.py` that set and check them. Keep its assertions about `PATH` and the runner's `chitty`, and rename it to drop `strips_worktree_environment` if nothing else is stripped.
- Leave `chitty.toml` alone: branches must not edit it. After this lands, the main checkout drops the `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT` prefix and its comment from `agent_command` and `[agent_commands]` there.

No property tests: this removes code, and the remaining behaviour (removing `CHITTY_USAGE_FILE`) is unchanged.

## Acceptance Criteria

- [ ] `git grep -n "VIRTUAL_ENV\|UV_PROJECT_ENVIRONMENT" -- src tests` finds nothing, except phrases in `tests/test_guide_read_only_cold_read.py` that do not concern the runner environment.
- [ ] A test shows that `chitty run` still removes `CHITTY_USAGE_FILE` from the agent environment (an existing one, or a new one if the deletions removed it). `make check` passes.

## History

- 2026-11-17T17:26:19Z kind-umber-toad → planning
