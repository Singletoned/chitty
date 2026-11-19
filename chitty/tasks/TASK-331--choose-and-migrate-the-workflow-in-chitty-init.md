---
title: Choose and migrate the workflow in chitty init
status: planning
labels:
  - needs-minor
priority: high
depends_on:
  - TASK-330
  - TASK-279
created: 2026-11-14
---

## Description

`chitty init` chooses and records the `workflow` setting from TASK-330 (`resolve_workflow`, `FIRST_WORKFLOW_VERSION` in `src/chitty/config.py`). Start after TASK-279 and TASK-321 land: they remove the Pi extension from `init_repo` and its config template in `src/chitty/store.py` and `src/chitty/config.py`.

- `chitty init --workflow tickets|runner` writes `workflow = "tickets"` or `workflow = "runner"`, replacing any existing `workflow` line. Without the option, an existing `workflow` line is kept.
- New repository, no option: write a tickets-only config: today's `INITIAL_CONFIG` without the `review = true` line and without the runner settings or their comments (`setup`, `check`, `agent_command`, `agent_timeout`, `work_model`, `review_model`, `error_reporter`, and the `[agent_commands]` table). Write `workflow = "tickets"` explicitly after the `chitty_version` line, so the choice does not depend on the version recorded (an unreleased `main` still reports the previous version). `--workflow runner` on a new repository writes today's config plus `workflow = "runner"`.
- Migration on an existing repository: add a pure function `add_runner_workflow(text: str, recorded_version: str | None, pyproject: bool) -> str`, beside the other `_add_missing_*` helpers in `store.py`. When the parsed config has no `workflow` key and `resolve_workflow(None, recorded_version)` is `"runner"`, it returns the text with `workflow = "runner"` added directly after the `chitty_version` line (in `[tool.chitty]` for `pyproject.toml`); otherwise it returns the text unchanged. `init_repo` calls it with the version recorded before it rewrites `chitty_version`, and prints one line when it changed the text. Without this, raising the version would silently turn a runner repository into a tickets one.
- Switching an existing repository to `runner` does not add or change `review`. If `review` is then unset or `false`, print one line saying reviews stay off until `review = true` is set.
- Change no other config line.
- Existing tests that set up a repository with `chitty init` and then exercise the runner (many in `tests/test_next.py`, `tests/test_landing.py` and others) will get `workflow = "tickets"`; make them pass `--workflow runner` rather than changing behaviour.
- Hypothesis is the property-testing tool; tests go in `tests/test_init_workflow.py`.

## Acceptance Criteria

- [ ] Property: for any generated config text (with or without a `workflow` line, in `chitty.toml` or `[tool.chitty]` form) and any `recorded_version` (`None` or one to four dot-separated non-negative integers), `add_runner_workflow` adds exactly one line, `workflow = "runner"`, when there is no `workflow` key and the version is `None` or older than `0.5.0`, and otherwise returns the text unchanged; the result parses, and every original line is still present in order. Fails today because the function does not exist.
- [ ] In a temp repository set up with `chitty_version = "0.4.2"` and no `workflow`, `chitty init` leaves `workflow = "runner"` and the new version in the config and prints one line about it; running `init` again changes nothing.
- [ ] `chitty init` in an empty temp repository writes a config containing `workflow = "tickets"` and no `review` or runner-setting lines (`setup`, `check`, `agent_command`, `agent_timeout`, `work_model`, `review_model`, `error_reporter`, `[agent_commands]`, comments included); `chitty init --workflow runner` there writes today's config plus `workflow = "runner"`.
- [ ] `--workflow tickets` and `--workflow runner` on an existing repository set the `workflow` line and change no other line; switching to `runner` with `review` unset prints the one line about reviews. `make check` passes.

## Notes

Planning 2026-11-19: raised to high. `0.5.0` was released without this (see `HUMAN-12`) and has been yanked; releases wait for this ticket. It has four criteria covering a new repository, migration and switching, and has never been cold-read: split it before cold reads.

## History

- 2026-11-14T18:21:54Z friendly-ginger-adder → planning
- 2026-11-14T18:23:27Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:25:42Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:30:19Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:30:31Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T19:22:00Z friendly-ginger-adder: changed description
- 2026-11-19T10:01:42Z quick-ginger-lapwing: changed priority, notes
