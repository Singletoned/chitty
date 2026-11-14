---
title: Choose and migrate the workflow in chitty init
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-330
created: 2026-11-14
---

## Description

`chitty init` chooses and records the `workflow` setting (from the ticket this depends on).

- `chitty init --workflow tickets|runner`. `runner` writes `workflow = "runner"`; `tickets` removes any `workflow` line, because `tickets` is the default. Without the option, an existing `workflow` value is kept.
- New repository, no option: write the tickets-only config. It has no `review` line and none of the runner settings or their comments (`setup`, `check`, `agent_command`, `agent_timeout`, `work_model`, `review_model`, `error_reporter`, `[agent_commands]`). `--workflow runner` on a new repository writes today's config plus `workflow = "runner"`.
- Existing repository with no `workflow` key and no option: if its config sets any runner setting listed above (with `[agent_commands]` counting only when non-empty), write `workflow = "runner"` and print one line saying so. Otherwise leave it as `tickets`.
- Switching an existing repository to `runner` does not add or change `review`. If `review` is then unset or `false`, print one line saying reviews stay off until `review = true` is set.
- Keep minimal diffs: change no other line of the config.

## Acceptance Criteria

- [ ] `chitty init --workflow runner` writes `workflow = "runner"`; `--workflow tickets` removes any `workflow` line; with no option an existing value is kept.
- [ ] On a new repository with no option, the written config has no `workflow` line, no `review` line, and no runner settings or their comments; with `--workflow runner` it is today's config plus `workflow = "runner"`.
- [ ] On an existing repository with no `workflow` key and no option, `workflow = "runner"` is written, with one printed line, exactly when the config sets a listed runner setting or a non-empty `[agent_commands]`; otherwise the config is unchanged.
- [ ] Switching to `runner` with `review` unset or `false` leaves `review` alone and prints one line saying reviews stay off.
- [ ] No other config line changes, shown by comparing the file before and after.
- [ ] CLI tests in temp repositories cover criteria 1 to 5, and fail without the change.

## History

- 2026-11-14T18:21:54Z friendly-ginger-adder → planning
