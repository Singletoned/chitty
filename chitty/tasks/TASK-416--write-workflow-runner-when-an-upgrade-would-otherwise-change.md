---
title: Write `workflow = "runner"` when an upgrade would otherwise change a runner repository to tickets
status: planning
labels:
  - blocks-release
priority: high
depends_on:
  - TASK-415
parent: TASK-331
created: 2026-11-19
---

## Description

Upgrading a repository raises its recorded `chitty_version`, and a config with no `workflow` line resolves its workflow from that version (`resolve_workflow` in `src/chitty/config.py`; `TASK-415` sets the boundary: at most `0.5.0` is `runner`). So once the installed version is past the boundary, an upgrade silently turns a runner repository into a tickets one, hiding `chitty run` and `chitty next`. That is what release `0.5.0` did on 2026-11-19. The upgrade must write `workflow = "runner"` first. Split out of `TASK-331`, which keeps the rest (new repositories, `--workflow`).

Upgrades happen in `init_repo` in `src/chitty/store.py`: from `chitty init`, and from `Repo._prepare_write`, which runs `init_repo` before any write in an `autocommit` repository whose recorded version differs from the installed one and commits the result as `chitty: upgrade repository setup`.

Decisions:

- Add a pure function to `src/chitty/store.py`, beside the `_add_missing_*` helpers: `add_runner_workflow(text: str, recorded_version: str | None, pyproject: bool) -> str`. The Chitty section is the same span `_add_missing_settings` uses: the top level of `chitty.toml` before its first table header, or the `[tool.chitty]` table of `pyproject.toml` up to the next header. When the section has no `workflow` key and `resolve_workflow(None, recorded_version)` is `"runner"`, it returns the text with one line `workflow = "runner"` inserted directly after the section's `chitty_version` line; otherwise it returns the text unchanged. When it must insert and the section has no `chitty_version` line, it raises `ChittyError` saying so. Keys named `workflow` or `chitty_version` outside the section (an `[agent_commands]` entry called `workflow`, a `[tool.other]` table) are ignored.
- `init_repo` calls it in the upgrade branch with the version recorded before the upgrade (`settings.get("chitty_version")`, `None` when absent), after `_add_missing_settings` (which adds a missing `chitty_version` line) and before the `re.sub` that rewrites `chitty_version`.
- Before writing the function, add it raising `NotImplementedError`, so the new tests fail on their own rather than at import.
- Out of scope, left in `TASK-331`: printing a line when the migration runs, new-repository configs, `--workflow`.

Tests, in a new `tests/test_init_workflow.py`, with Hypothesis, the repository's property-testing tool:

- Generator for configs: a Chitty section made of lines drawn from `format = 1`, `default_context = "tasks"`, `autocommit = true`, `review = true`, `# a comment` and a blank line, in drawn order, with the `chitty_version = <version>` line at a drawn position, the version written with `json.dumps` so any drawn text stays valid TOML, and optionally a `workflow = "runner"` or `workflow = "tickets"` line at a drawn position. For `chitty.toml`, the section is followed by `[contexts.tasks]` with `prefix = "TASK"`, and optionally `[agent_commands]` with `workflow = "pi -p {prompt}"`. For `pyproject.toml`, `[project]` with `name = "x"` comes first, then `[tool.chitty]` and the section, then optionally `[tool.other]` with `workflow = "tickets"` and `chitty_version = "9.9.9"`. Versions are drawn from `VERSIONS` in `tests/test_config_workflow.py` plus `0.4.2`, `0.5.0` and `0.5.1`; `recorded_version` is the drawn version (what `tomllib` reads back from the line). The expected workflow comes from `resolve_workflow`, which `TASK-415` tests.
- Existing tests that compare an upgraded config with exact expected text gain the new line when their recorded version is at most `0.5.0` and they have no `workflow` line; update their expected text rather than the behaviour.

## Acceptance Criteria

- [ ] Property (Hypothesis), using the generator in Tests: when the section has no `workflow` key and the recorded version resolves to `runner`, the result has exactly one more line than the input, `workflow = "runner"`, directly after the section's `chitty_version` line, every other line is unchanged and in order, and `tomllib` reads `workflow` as `runner` from the Chitty section; otherwise the result equals the input. Applying the function twice equals applying it once
- [ ] In a temporary Git repository with `autocommit = true`, `chitty_version = "0.4.2"` and no `workflow` line: `chitty init` leaves a `workflow = "runner"` line and the installed version in the file, and a second `chitty init` leaves the file byte for byte the same; in a second such repository, `chitty add` commits `chitty: upgrade repository setup` with the `workflow = "runner"` line. Both fail before the change, on the line check
- [ ] `make check` passes

## History

- 2026-11-19T10:50:03Z quick-ginger-lapwing → planning
- 2026-11-19T10:50:14Z quick-ginger-lapwing: changed description
