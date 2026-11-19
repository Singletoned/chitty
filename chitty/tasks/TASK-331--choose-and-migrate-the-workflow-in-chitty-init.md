---
title: Choose and migrate the workflow in chitty init
status: planning
labels:
  - needs-minor
priority: high
depends_on:
  - TASK-330
  - TASK-279
  - TASK-416
created: 2026-11-14
---

## Description

`chitty init` chooses and records the `workflow` setting from TASK-330 (`resolve_workflow`, `FIRST_WORKFLOW_VERSION` in `src/chitty/config.py`). Start after TASK-279 and TASK-321 land: they remove the Pi extension from `init_repo` and its config template in `src/chitty/store.py` and `src/chitty/config.py`.

- `chitty init --workflow tickets|runner` writes `workflow = "tickets"` or `workflow = "runner"`, replacing any existing `workflow` line. Without the option, an existing `workflow` line is kept.
- New repository, no option: write a tickets-only config: today's `INITIAL_CONFIG` without the `review = true` line and without the runner settings or their comments (`setup`, `check`, `agent_command`, `agent_timeout`, `work_model`, `review_model`, `error_reporter`, and the `[agent_commands]` table). Write `workflow = "tickets"` explicitly after the `chitty_version` line, so the choice does not depend on the version recorded (an unreleased `main` still reports the previous version). `--workflow runner` on a new repository writes today's config plus `workflow = "runner"`.
- Migration on an existing repository (`add_runner_workflow`, called from `init_repo`) moved to `TASK-416`; this ticket builds on it. Printing a line when the migration changes the config stays here.
- Switching an existing repository to `runner` does not add or change `review`. If `review` is then unset or `false`, print one line saying reviews stay off until `review = true` is set.
- Change no other config line.
- Existing tests that set up a repository with `chitty init` and then exercise the runner (many in `tests/test_next.py`, `tests/test_landing.py` and others) will get `workflow = "tickets"`; make them pass `--workflow runner` rather than changing behaviour.
- Hypothesis is the property-testing tool; tests go in `tests/test_init_workflow.py`.

## Acceptance Criteria

- [ ] `chitty init` in an empty temp repository writes a config containing `workflow = "tickets"` and no `review` or runner-setting lines (`setup`, `check`, `agent_command`, `agent_timeout`, `work_model`, `review_model`, `error_reporter`, `[agent_commands]`, comments included); `chitty init --workflow runner` there writes today's config plus `workflow = "runner"`.
- [ ] `--workflow tickets` and `--workflow runner` on an existing repository set the `workflow` line and change no other line; switching to `runner` with `review` unset prints the one line about reviews. `make check` passes.

## Notes

Planning 2026-11-19: raised to high. `0.5.0` was released without this (see `HUMAN-12`) and has been yanked; releases wait for this ticket. It has four criteria covering a new repository, migration and switching, and has never been cold-read: split it before cold reads.

Planning 2026-11-19: split. The upgrade migration (old criteria 1 and 2) is `TASK-416`, needed for `0.5.1`; the boundary is `TASK-415` (done). What is left here (new-repository config, `--workflow`, the printed line) is not needed for `0.5.1`.

## History

- 2026-11-14T18:21:54Z friendly-ginger-adder → planning
- 2026-11-14T18:23:27Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:25:42Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:30:19Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:30:31Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T19:22:00Z friendly-ginger-adder: changed description
- 2026-11-19T10:01:42Z quick-ginger-lapwing: changed priority, notes
- 2026-11-19T11:05:50Z quick-ginger-lapwing: changed dependencies, description, acceptance criteria, notes
