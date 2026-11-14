---
title: Add a workflow setting, tickets by default
status: todo
labels:
  - needs-minor
priority: medium
created: 2026-11-14
---

## Description

Chitty was meant to be a plain ticketing system; the runner pipeline (worktrees, review, landing, role guides) is a layer on top. Add a `workflow` setting that chooses between them, with `tickets` as the default for repositories set up at `0.5.0` or later. Until TASK-331, `chitty init` still writes `review = true` and no `workflow`.

- `workflow` in `chitty.toml` or `[tool.chitty]`: `"tickets"` or `"runner"`. Any other value, or a non-string, is a config error naming `workflow` and both allowed values.
- Add a pure function `resolve_workflow(workflow: str | None, chitty_version: str | None) -> str` in `src/chitty/config.py`, and a module constant `FIRST_WORKFLOW_VERSION = "0.5.0"` there. An explicit `workflow` is returned as is. A missing one gives `"runner"` when `chitty_version` is `None`, cannot be read by `version_key`, or compares older than `FIRST_WORKFLOW_VERSION` with `version_key` (a plain tuple compare, so `"0.5"` is older and `"0.5.0.0"` is not), and `"tickets"` otherwise. It never raises: an unreadable `chitty_version` keeps its existing warning (`recorded version cannot be read`, tested by `TestSetupVersion` in `tests/test_cli.py`) and loads as `runner`. A non-string `chitty_version` gives only its existing type error, with no second error about `workflow`. Every config older than that was set up for the runner, so it keeps its behaviour. The `needs-minor` label makes this ticket's release `0.5.0`.
- The loaded `RepoConfig` exposes the resolved value as `config.workflow` (always `"tickets"` or `"runner"`, never `None`).
- `config.review` stays a resolved `bool`, never `None`, so existing callers and tests that read it keep working. Its default depends on the workflow: `false` under `tickets`, `true` under `runner`. An explicit repository `review` wins under either, and a context's `review` still overrides the repository value; `Repo.review_required` in `src/chitty/store.py` is the caller to keep correct.
- Docs: in `docs/plan/config.md`, document `workflow` and record that this deliberately breaks its rule that new defaults keep existing behaviour (only for repositories set up at `0.5.0` or later). In `docs/plan/direction.md`, record that tickets-only is Chitty's original purpose and the runner an optional layer.
- Out of scope: `chitty init` (its config template still writes `review = true`; TASK-331 changes it), the managed block, and hiding commands or guides.
- The cold read resolved `workflow` and `review` in a `mode="before"` model validator that fills them in the input when absent and passes `None` to `resolve_workflow` for a non-string `chitty_version`; that keeps the frozen model and gives a single type error.
- Tests: Hypothesis is the property-testing tool; put them in `tests/test_config_workflow.py`.

## Acceptance Criteria

- [ ] Property: for any `v` that is `None`, a string of one to four dot-separated non-negative integers, or any other text, `resolve_workflow(None, v)` is `"runner"` exactly when `v` is `None`, unreadable by `version_key`, or `version_key(v) < version_key("0.5.0")`, and `"tickets"` otherwise; it never raises; and for each explicit `w` in (`"tickets"`, `"runner"`) and every such `v`, `resolve_workflow(w, v) == w`. The property test also checks the boundary values `0.4.9`, `0.5`, `0.5.0` and `0.5.0.0` explicitly (Hypothesis `@example`). Fails today because the function does not exist.
- [ ] Loading a temp repository config: no `workflow` with `chitty_version = "0.4.2"`, `"0.5.0"`, `"1.0rc1"`, and none gives `config.workflow` of `runner`, `tickets`, `runner`, `runner`; `workflow = "bogus"` and `workflow = 1` fail with an error naming `workflow`, `tickets` and `runner`; `chitty_version = 1` fails with an error that does not mention `workflow`. Existing `tests/test_config.py` and `TestSetupVersion` in `tests/test_cli.py` pass unchanged.
- [ ] For every combination of workflow (`tickets`, `runner`), repository `review` (unset, `true`, `false`) and context `review` (unset, `true`, `false`), `config.review` is the repository value if set, else `false` under `tickets` and `true` under `runner`; and `Repo.review_required` returns the context value if set, else `config.review`. A small fixed set of 18 cases, each tested, so no property is needed. The `tickets` with both unset case fails today.
- [ ] `docs/plan/config.md` documents `workflow`, `FIRST_WORKFLOW_VERSION` and the changed-default decision; `docs/plan/direction.md` records that tickets-only is the original purpose; `make check` passes.

## Notes

Replanned with the human on 2026-11-14. The original ask (agents feel they must write tickets for a weaker agent and cannot review their own) is solved by a tickets-only workflow chosen at install time, not by an exploratory agent mode. Stages: this ticket (setting), then `chitty init` with migration, then the managed block, hidden runner commands and hidden role guides. Earlier cold-read questions about `chitty run` invocation no longer apply.

Cold read starting point: `refs/cold-read/TASK-330/2` (a Haiku implementing read against this text, `make check` green). Its files: `src/chitty/config.py`, `tests/test_config_workflow.py`, `docs/plan/config.md`, `docs/plan/direction.md`; see them with `git show refs/cold-read/TASK-330/2:<path>`. Check it against the current criteria rather than trusting it.

## History

- 2026-11-14T13:39:35Z jolly-umber-badger → planning
- 2026-11-14T13:40:56Z jolly-umber-badger: changed notes
- 2026-11-14T18:21:52Z friendly-ginger-adder: replaced notes; changed title, labels, description, acceptance criteria
- 2026-11-14T18:23:25Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:28:28Z friendly-ginger-adder: changed title, description, acceptance criteria
- 2026-11-14T18:28:41Z friendly-ginger-adder: changed owner
- 2026-11-14T18:28:41Z friendly-ginger-adder planning → cold-read
- 2026-11-14T18:33:59Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:33:59Z friendly-ginger-adder cold-read → planning
- 2026-11-14T18:34:00Z friendly-ginger-adder planning → cold-read
- 2026-11-14T18:37:15Z friendly-ginger-adder: changed description, acceptance criteria, notes
- 2026-11-14T18:37:15Z friendly-ginger-adder cold-read → planning
- 2026-11-14T18:37:17Z friendly-ginger-adder: changed owner
- 2026-11-14T18:37:17Z friendly-ginger-adder planning → todo
