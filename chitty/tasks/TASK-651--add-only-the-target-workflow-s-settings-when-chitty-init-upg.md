---
title: Add only the target workflow's settings when `chitty init` upgrades a config
status: todo
priority: high
parent: TASK-331
created: 2026-11-24
---

## Description

When `chitty init` upgrades an existing config, add only the settings its workflow uses. Today `_add_missing_settings` in `src/chitty/store.py` adds `review = true` and six commented runner lines, and `_add_missing_agent_commands_table` adds `[agent_commands]`, on every upgrade, whatever the workflow. So an upgrade of a tickets-only config turns it into a runner one, and an upgrade of a runner config switches reviews on with an active `review = true`. Split from `TASK-331` on 2026-11-24, which builds `chitty init --workflow` on top of this; the rules below are the owner's decision recorded there (2026-11-22, option B plus a commented review line).

Decisions:

- `_add_missing_settings(text, settings, pyproject, project, *, workflow: str)`: a new keyword-only `workflow` parameter, with no default. Its two callers in tests (`tests/test_cli.py` `test_init_escapes_added_project_settings` and `tests/test_pi_retirement.py`) pass `workflow="runner"`.
- `workflow == "tickets"`: add only the `project`, `chitty_version` and `archive` lines, when missing, as today. Add no `review` line and none of the six commented runner lines (`setup`, `check`, `agent_command`, `work_model`, `review_model`, `rebase_model`).
- `workflow == "runner"`: as today, except the `review` addition. Instead of `review = true`, add `# review = true`, and add it only when the Chitty section (the `section` text `_add_missing_settings` already computes, never the whole file, which has `review = false` under `[contexts.human]`) has no line matching `^[ \t]*#?[ \t]*review[ \t]*=`. So a commented or active `review` line, `true` or `false`, stops it, and a repeated upgrade adds nothing. The rules for the six commented runner lines are unchanged, including the whole-file `f"{key} =" in text` check for `setup`, `check` and `agent_command`; that a spelling such as `#setup="x"` is not detected is an existing quirk, out of scope. Additions keep today's order (`project`, `chitty_version`, `archive`, `review`, `setup`, `check`, `agent_command`, `work_model`, `review_model`, `rebase_model`) and place: one block before the first table header (or the end of the `[tool.chitty]` section), followed by one blank line.
- `init_repo`, upgrade branch: the target workflow is `config.workflow`, from the `load_repo_config(directory)` already called there, which resolves a missing `workflow` line from the recorded `chitty_version` (`resolve_workflow` and `LAST_RUNNER_DEFAULT_VERSION` in `src/chitty/config.py`). Pass it to `_add_missing_settings`, and call `_add_missing_agent_commands_table` only when it is `runner`. Leave `add_runner_workflow`, `_add_missing_human_review`, `_add_missing_backlog_context` and the new-repository branch (which writes `INITIAL_CONFIG`) unchanged.
- Out of scope, left to `TASK-331`: `chitty init --workflow`, the tickets-only config for a new repository, and any printed line about reviews.

Tests, in `tests/test_init_workflow.py`, using Hypothesis (the repository's property tool) with `@settings(max_examples=examples(50))`, `examples` from `tests/__init__.py`, as in `tests/test_due_date.py`:

- Property `test_upgrade_adds_only_the_workflow_settings`. A new strategy `upgrade_cases()` draws: `pyproject` (bool); `workflow` from `("tickets", "runner")`; for `review`, one of absent, `review = true`, `review = false`, `# review = true`, `#review=false`; for each of the six runner keys, one of absent, active (`<key> = "x"`), or commented (`# <key> = "x"`); whether `project = "p"` and `archive = "move"` are present. The section always has `chitty_version = "0.7.0"`; draw the order of its lines with `st.permutations`. Wrap it as `config_cases()` does: for `pyproject`, `[project]\nname = "x"\nreview = true\n[tool.chitty]\n` before it and `[tool.other]\nreview = true\n` after; otherwise `[contexts.tasks]\nprefix = "TASK"\n[contexts.human]\nprefix = "HUMAN"\nreview = false\n` after. `upgrade_cases()` returns the text together with every drawn state, and each `@example` gives that same tuple. These outer `review` lines are distractors that must not stop the `# review = true` addition. Call `_add_missing_settings(text, settings, pyproject, "p", workflow=workflow)`, with `settings` the section parsed by `tomllib`. Commented runner keys are drawn only in the `# <key> = "x"` spelling, and no runner key appears outside the section, so the existing detection rules decide every case. Expected: with `additions` the expected lines, in the order above, each exactly the string `_add_missing_settings` writes today (with `# review = true` in place of `review = true`), the result is `text[:position] + "\n".join(additions) + "\n\n" + text[position:]`, where `position` is the start of the first table header after the section, or the end of the file; with no additions, the result is the input. For `tickets`, the block holds only the missing ones of the `project`, `chitty_version` and `archive` lines. For `runner`, it also holds `# review = true` exactly when the drawn `review` state is absent, and the commented line for each runner key drawn absent; it never holds a line matching `^review[ \t]*=`. The result parses with `tomllib`, and applying `_add_missing_settings` again, with `settings` re-parsed from the result, returns it unchanged.
- Add `@example` cases for these wrong versions, each of which the property must reject: `workflow` ignored (tickets case with every key absent); `review = true` still added (runner, review absent); `"review" not in settings` used instead of the regex (runner, review `# review = true`); the whole file searched for `review` (runner, review absent, non-pyproject, so only `[contexts.human]` has `review = false`); a substring `"review" in section` check (runner, review absent, `review_model` active).
- CLI examples, in `TestUpgradeWorkflow` (its `setUp` writes `CONFIG` from `tests/support.py` without its `workflow` line and with `chitty_version = "0.4.2"`; `invoke` runs with `CHITTY_VERSION` patched to `0.5.1`). (1) `init`: the config gains `workflow = "runner"`, `# review = true`, `# setup`, `# work_model`, `# review_model` and `# rebase_model` lines (it already has `check` and `agent_command`), and ends with `[agent_commands]`; its top-level `tomllib` data has no `review` key; a second `init` changes nothing. (2) A new test that first replaces `chitty_version = "0.4.2"` with `chitty_version = "0.5.1"` and commits: `init` adds no `workflow` line, the text before the first table header gains only the `project` and `archive` lines, and the file has no `[agent_commands]` table. The `review = false` under `[contexts.human]` and the `[contexts.backlog]` table that `_add_missing_human_review` and `_add_missing_backlog_context` add are expected, as today; a second `init` changes nothing. (3) As (2), but with `chitty_version = "0.4.2"` kept and `workflow = "tickets"` added after it: the same result as (2), because an explicit `workflow` line decides the target, not the version.

`_add_missing_settings` exists, so a stub cannot show the tests fail. Before implementing, add the `workflow` keyword, accepted and ignored, update the callers, and run the new tests: the property (through its `@example` cases) and both CLI examples except the stability checks must fail. Record that run in a note, then implement and run `make check`.

## Acceptance Criteria

- [ ] The `upgrade_cases()` property `test_upgrade_adds_only_the_workflow_settings` passes, and a recorded run with `workflow` accepted but ignored shows it failing
- [ ] CLI examples (1), (2) and (3) in `TestUpgradeWorkflow` pass: a runner upgrade adds the commented settings, `# review = true` and `[agent_commands]` but no active `review`; a tickets upgrade, whether from the recorded version or an explicit `workflow` line, adds none of them; a second `init` changes nothing
- [ ] `make check` passes, with the two existing `_add_missing_settings` callers passing `workflow="runner"`

## History

- 2026-11-24T07:41:58Z sunny-hazel-gannet → planning
- 2026-11-24T07:42:34Z sunny-hazel-gannet planning → cold-read
- 2026-11-24T07:44:30Z sunny-hazel-gannet: changed description
- 2026-11-24T07:44:30Z sunny-hazel-gannet cold-read → planning
- 2026-11-24T07:44:34Z sunny-hazel-gannet planning → cold-read
- 2026-11-24T07:46:35Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T07:46:35Z sunny-hazel-gannet cold-read → planning
- 2026-11-24T07:46:38Z sunny-hazel-gannet planning → todo
