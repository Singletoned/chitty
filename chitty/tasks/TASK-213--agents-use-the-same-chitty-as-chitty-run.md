---
title: Agents use the same `chitty` as `chitty run`
status: doing
priority: high
created: 2026-11-06
---

## Description

Every Chitty write to a ticket should come from one Chitty version: the one running `chitty run`, from the main checkout. In this repository it doesn't. `agent_command` and `[agent_commands].claude` in `chitty.toml` wrap the agent in `uv run --no-sync`, which puts the ticket worktree's `.venv/bin` first on `PATH`, so the agent's bare `chitty` is the branch's code. The comment above `agent_command` says this is deliberate. The human decided on 2026-11-06 that it's a bug: the branch's code is unreviewed, it may be a different version, and it can write ticket state that `main`'s Chitty then can't read (`TASK-204`).

Changes, all in `src/chitty/run.py` plus docs:
1. Find the runner's own executable as `Path(sys.executable).parent / "chitty"`, the script installed beside the running interpreter. Don't use `shutil.which`, which can find a different `chitty` earlier on `PATH`. Fail loudly with `ChittyError` if that file doesn't exist.
2. Pass the agent an explicit `env=`, built immediately before the agent's `subprocess.run`, so variables set just before it (such as `CHITTY_USAGE_FILE`) are kept. Copy `os.environ`, put that directory first on `PATH`, and remove `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT`, which the `env -u` in today's agent commands removes. The agent's `make` targets still use the worktree's `.venv`, because the `Makefile` sets `PATH`, `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` itself.
3. Update the `chitty run` section of `README.md` and "Next action and runner" in `PLAN.md`. Without the wrapper, `pi` and `claude` come from the global `PATH`, which is intended.

Not on the branch: removing `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync` from this repository's `agent_command` and `[agent_commands].claude`, and their comment. Branches must not change `chitty.toml` (`TASK-212`), so a human-run session makes that change on the main checkout after this lands. Write that in the ticket's summary as the follow-up.

Out of scope: running the agent in a container.

## Acceptance Criteria

- [ ] A test runs `chitty run` with a fake agent and a different fake `chitty` placed first on `PATH`, standing in for a branch's. The agent records which `chitty` its `PATH` resolves to, and its `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT`. The test asserts it resolves to `Path(sys.executable).parent / "chitty"`, that both variables are unset even when the runner had them, and that `CHITTY_USAGE_FILE` is still passed. It fails before the fix.
- [ ] `README.md` and `PLAN.md` say the agent uses the runner's `chitty`, `chitty.toml` is unchanged on the branch, and `make check` passes.

## Plan

1. Inspect run.py and existing runner tests, then add a regression test that places a fake branch chitty first on PATH and verifies the runner executable, stripped environment variables, and usage file propagation.
2. Update run.py to resolve the chitty executable beside sys.executable and pass a freshly copied environment with that directory first on PATH and virtual-environment variables removed.
3. Update the runner documentation in README.md and PLAN.md without touching chitty.toml, run format/check, and commit the implementation with Task: TASK-213.

## Notes

Under `TASK-212`, a branch may not change `chitty.toml`. The `agent_command` and `[agent_commands]` edit in item 2 must be done on the main checkout by a human-run session after this lands, not on the branch. Settle this with the cold-read findings.

Cold read 1 (Sonnet, `refs/cold-read/TASK-213/1`; the test failed before and passed after; `make check` OK). Outcomes:
- Criterion 1 couldn't be built as written: fixed, the test now puts a fake `chitty` first on `PATH`.
- `shutil.which` is fragile: fixed, use `Path(sys.executable).parent / "chitty"`, which also removes the test suite's dependence on `PATH`.
- `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` would leak into the agent: fixed, they're stripped.
- When to build the environment: fixed, immediately before `subprocess.run`, after the reader's first version lost `CHITTY_USAGE_FILE`.
- The `chitty.toml` edit: moved off the branch under `TASK-212`, to be done on `main` after landing.
- `pi` and `claude` now come from the global `PATH`: accepted, that's intended.
- No version bump: confirmed.
The reader's ref follows the old scope (it edits `chitty.toml` and uses `which`), so it was deleted.

## History

- 2026-11-06T16:24:16Z youthful-toad → backlog
- 2026-11-06T16:44:15Z youthful-toad: changed notes
- 2026-11-06T16:46:07Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T16:46:07Z youthful-toad backlog → todo
- 2026-11-06T20:00:29Z mellow-falcon todo → doing
- 2026-11-06T20:00:50Z mellow-falcon: wrote the plan
