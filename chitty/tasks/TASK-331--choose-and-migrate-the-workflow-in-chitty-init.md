---
title: Choose and migrate the workflow in chitty init
status: cold-read
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

`chitty init` should let a person choose the `workflow` setting (`tickets` or `runner`) and give new repositories a tickets-only config. `resolve_workflow` and `LAST_RUNNER_DEFAULT_VERSION` (`0.5.0`) in `src/chitty/config.py` already make a config with no `workflow` line resolve to `tickets` at today's version, and `add_runner_workflow` in `src/chitty/store.py` (`TASK-416`) already records `workflow = "runner"` when upgrading a config from `0.5.0` or earlier. `TASK-279` and `TASK-321` have landed. Rechecked against `main` on 2026-11-21.

Decisions:

- New pure function `set_workflow(text: str, workflow: str, pyproject: bool) -> str` in `src/chitty/store.py`, next to `add_runner_workflow` and finding the section the same way (`[tool.chitty]` up to the next table header when `pyproject`, else the text before the first table header). If the section has a `workflow = ...` line, replace that whole line with `workflow = "<workflow>"`; otherwise insert that line directly after the `chitty_version` line, as `add_runner_workflow` does, raising the same `ChittyError` when there is no `chitty_version` line. Commented lines such as `# workflow = "tickets"` are not setting lines and are left alone.
- `chitty init --workflow [tickets|runner]` (a `click.Choice`). With the option, `init_repo` applies `set_workflow` to the config it writes or upgrades, after `add_runner_workflow`. Without it, an existing `workflow` line is kept. `init_repo` gains a keyword-only `workflow: str | None` parameter, with no default, passed by `cli.py`; update its other callers to pass `workflow=None`.
- The `AGENTS.md` managed block is rendered for the workflow the config will have after the change. Today `init_repo` takes the workflow from the existing config (or `resolve_workflow(None, CHITTY_VERSION)` for a new one) and calls `_managed_agents` before writing anything, so damaged markers fail before any write. Keep that early call for validation, and when `--workflow` is given use its value as the workflow passed to `_managed_agents` there; with no option the current rule stands.
- New repository, no option: write `INITIAL_CONFIG` without its top-level `review = true` line, without the commented runner lines (`# setup`, `# check`, `# agent_command`, `# work_model`, `# review_model`, `# rebase_model`), and without the `[agent_commands]` table; add `workflow = "tickets"` directly after the `chitty_version` line. Keep `review = false` under `[contexts.human]`, and every other line. `--workflow runner` on a new repository writes today's `INITIAL_CONFIG` plus `workflow = "runner"` after `chitty_version`. Implement this as two templates or one template with the runner lines removed; either is fine as long as the bytes match these rules.
- Upgrading a config whose workflow resolves to `tickets` (after `set_workflow`, using `resolve_workflow` with the section's `workflow` and recorded `chitty_version`) adds none of the runner settings: `_add_missing_settings` skips its `review`, `setup`, `check`, `agent_command`, `work_model`, `review_model` and `rebase_model` additions, and `_add_missing_agent_commands_table` is not called. It still adds `project`, `chitty_version` and `archive` when missing. Today both add those lines on every upgrade, so a second `chitty init` would turn a tickets-only config back into a runner one. Pass the resolved workflow into `_add_missing_settings` as a keyword-only argument with no default.
- Switching to, or upgrading, a config whose workflow resolves to `runner` (owner decision 2026-11-22, option B plus a commented review line): add the six commented runner lines and the `[agent_commands]` table when missing, as today, and never add an active `review` line. Where `_add_missing_settings` adds `review = true` today, it adds `# review = true` instead, and skips it when the section already has a line containing `review =` (commented or not), so a repeated `init` adds nothing. With no `review` line the runner reviews anyway (`_workflow_defaults` in `src/chitty/config.py` defaults `review` to `workflow == "runner"`), so the commented line only documents that default. If the resulting config's top-level `review` is `false`, print exactly `reviews stay off until review = true is set in <config path>` to stdout; with it unset or `true`, print nothing about reviews.
- Not built (decided 2026-11-21): a printed line when `add_runner_workflow` changes the config during an upgrade. The upgrade already writes the setting, and `TASK-416` shipped without it.
- Change no other config line. `--workflow runner` on a new repository keeps today's active `review = true` from `INITIAL_CONFIG`.

Tests: in `tests/test_init_workflow.py`.

- Property `test_set_workflow_changes_only_the_workflow_line`, Hypothesis (the repository's property tool), reusing `config_cases()` from that file and and drawing a separate target workflow from `("tickets", "runner")` (the case's fifth element is the existing `workflow` line's value, or `None`). Expected, computed from the drawn case: when the case has a `workflow` line, the result's lines equal the input's with that one line replaced; otherwise the input's lines with `workflow = "<w>"` inserted at `version_index + 1`. The result parses with `tomllib` and its section's `workflow` is the drawn value; other tables (`[tool.other]`, `[agent_commands]`) are unchanged; applying `set_workflow` again gives the same text.
- CLI examples with `CliRunner`, each in an empty temporary Git repository (as `TestUpgradeWorkflow` sets up, without writing `chitty.toml`): (1) `init`: the config has `workflow = "tickets"` directly after `chitty_version`, no top-level `review` line, none of the six runner comment lines and no `[agent_commands]`, and keeps `[contexts.human]` with `review = false`; running `init` again leaves `chitty.toml` and `AGENTS.md` byte-for-byte unchanged. (2) `init --workflow runner`: the config equals the `INITIAL_CONFIG` rendering plus the `workflow = "runner"` line. (3) after (1), `init --workflow runner`: the `workflow` line changes, the six commented runner lines, `# review = true` and `[agent_commands]` are added, every other line is unchanged, no reviews line is printed, `AGENTS.md`'s managed block is the runner block (`managed_guide("runner")`), and a second `init` changes nothing. (4) after (2), `init --workflow tickets`: only the `workflow` line changes, and no reviews line is printed. (5) after (1), add `review = false` after the `workflow` line, then `init --workflow runner`: stdout has the reviews line.
- Existing tests that run `chitty init` and then use the runner commands (`run`, `next`) now get `workflow = "tickets"`; make them pass `--workflow runner` rather than changing behaviour.

Before implementing, add `set_workflow` raising `NotImplementedError` and run the new tests to confirm they fail; then implement and run `make check`.

## Acceptance Criteria

- [ ] The `set_workflow` property passes, and fails against the `NotImplementedError` stub
- [ ] CLI examples (1) and (2) pass: a new repository gets the tickets-only config (and a repeat `init` changes nothing), or with `--workflow runner` today's config plus `workflow = "runner"`
- [ ] CLI examples (3), (4) and (5) pass: switching adds only the documented lines (commented runner settings, `# review = true`, `[agent_commands]`) or, to `tickets`, only changes the `workflow` line; it re-renders the managed block, a repeated `init` changes nothing, and the reviews line is printed only for `review = false`; `make check` passes

## Notes

Planning 2026-11-19: raised to high. `0.5.0` was released without this (see `HUMAN-12`) and has been yanked; releases wait for this ticket. It has four criteria covering a new repository, migration and switching, and has never been cold-read: split it before cold reads.

Planning 2026-11-19: split. The upgrade migration (old criteria 1 and 2) is `TASK-416`, needed for `0.5.1`; the boundary is `TASK-415` (done). What is left here (new-repository config, `--workflow`, the printed line) is not needed for `0.5.1`.

Question for the owner (2026-11-21, overnight planner): when an existing tickets-only repository switches with `chitty init --workflow runner`, the normal upgrade steps (`_add_missing_settings`, `_add_missing_agent_commands_table` in `src/chitty/store.py`) would add `review = true`, the six commented runner lines and `[agent_commands]`, either during the switch or on the next plain `chitty init`. The ticket says the switch changes no other line and prints `reviews stay off until review = true is set`. Which do you want? (A) The switch changes only `workflow`, and later `init` runs never add `review` to a config recorded after `0.5.0` (they may add the comments and table). (B) The switch also adds the commented runner lines and `[agent_commands]`, but never `review`. (C) Something else. Everything else in the ticket is settled; one cold read done, its other findings applied.

Owner answer, 2026-11-22: option B, plus a commented-out review line. Planner: the old printed-line rule ("unset or false") was wrong, since an unset `review` means reviews are on under `runner`; now it prints only for `review = false`.

## History

- 2026-11-14T18:21:54Z friendly-ginger-adder → planning
- 2026-11-14T18:23:27Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:25:42Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:30:19Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:30:31Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T19:22:00Z friendly-ginger-adder: changed description
- 2026-11-19T10:01:42Z quick-ginger-lapwing: changed priority, notes
- 2026-11-19T11:05:50Z quick-ginger-lapwing: changed dependencies, description, acceptance criteria, notes
- 2026-11-21T23:12:15Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:12:15Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:16:09Z lively-zinc-newt: changed description
- 2026-11-21T23:16:09Z lively-zinc-newt cold-read → planning
- 2026-11-21T23:16:27Z lively-zinc-newt: changed labels, notes
- 2026-11-22T11:14:48Z friendly-jade-stoat: changed labels, description, acceptance criteria, notes
- 2026-11-22T11:14:48Z friendly-jade-stoat planning → cold-read
