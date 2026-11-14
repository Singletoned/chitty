---
title: Choose and migrate the workflow in chitty init
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-330
  - TASK-279
created: 2026-11-14
---

## Description

`chitty init` chooses and records the `workflow` setting (from the ticket this depends on, including how a missing `workflow` is resolved from `chitty_version`).

- `chitty init --workflow tickets|runner` writes `workflow = "tickets"` or `workflow = "runner"`. Without the option, an existing `workflow` value is kept.
- New repository, no option: write the tickets-only config. It has no `workflow` line, no `review` line, and none of the runner settings or their comments (`setup`, `check`, `agent_command`, `agent_timeout`, `work_model`, `review_model`, `error_reporter`, `[agent_commands]`). `--workflow runner` on a new repository writes today's config plus `workflow = "runner"`.
- Migration: when `init` would raise `chitty_version` from missing or older than `FIRST_WORKFLOW_VERSION` to that version or later, and the config has no `workflow` key and no option was given, write `workflow = "runner"` in the same edit and print one line saying so. Otherwise bumping the version would silently turn a runner repository into a tickets one.
- Switching an existing repository to `runner` does not add or change `review`. If `review` is then unset or `false`, print one line saying reviews stay off until `review = true` is set.
- Keep minimal diffs: change no other line of the config.

## Acceptance Criteria

- [ ] `chitty init --workflow runner` writes `workflow = "runner"` and `--workflow tickets` writes `workflow = "tickets"`; with no option an existing value is kept.
- [ ] On a new repository with no option, the written config has no `workflow` line, no `review` line, and no runner settings or their comments; with `--workflow runner` it is today's config plus `workflow = "runner"`.
- [ ] On an existing repository whose `chitty_version` is missing or older than `FIRST_WORKFLOW_VERSION`, with no `workflow` key and no option, `init` writes `workflow = "runner"` alongside the version bump and prints one line; a repository already at or past that version is not given a `workflow` line.
- [ ] Switching to `runner` with `review` unset or `false` leaves `review` alone and prints one line saying reviews stay off.
- [ ] No other config line changes, shown by comparing the file before and after.
- [ ] CLI tests in temp repositories cover criteria 1 to 5, and fail without the change.

## History

- 2026-11-14T18:21:54Z friendly-ginger-adder → planning
- 2026-11-14T18:23:27Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:25:42Z friendly-ginger-adder: changed dependencies
