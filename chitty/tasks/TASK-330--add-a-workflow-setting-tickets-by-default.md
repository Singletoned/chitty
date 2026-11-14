---
title: Add a workflow setting, tickets by default
status: cold-read
labels:
  - needs-minor
priority: medium
owner: friendly-ginger-adder
created: 2026-11-14
---

## Description

Chitty was meant to be a plain ticketing system; the runner pipeline (worktrees, review, landing, role guides) is a layer on top. Add a `workflow` setting that chooses between them, with `tickets` as the default for newly set-up repositories.

- `workflow` in `chitty.toml` or `[tool.chitty]`: `"tickets"` or `"runner"`. Any other value, or a non-string, is a config error naming `workflow` and both allowed values.
- Add a pure function `resolve_workflow(workflow: str | None, chitty_version: str | None) -> str` in `src/chitty/config.py`, and a module constant `FIRST_WORKFLOW_VERSION = "0.5.0"` there. An explicit `workflow` is returned as is. A missing one gives `"runner"` when `chitty_version` is `None` or compares older than `FIRST_WORKFLOW_VERSION` with the existing `version_key`, and `"tickets"` otherwise. Every config older than that was set up for the runner, so it keeps its behaviour. The `needs-minor` label makes this ticket's release `0.5.0`.
- The loaded `RepoConfig` exposes the resolved value as `config.workflow` (always `"tickets"` or `"runner"`, never `None`).
- The repository `review` default depends on the workflow: `false` under `tickets`, `true` under `runner`. An explicit repository `review` wins under either, and a context's `review` still overrides the repository value; `Repo.review_required` in `src/chitty/store.py` is the caller to keep correct.
- Docs: in `docs/plan/config.md`, document `workflow` and record that this deliberately breaks its rule that new defaults keep existing behaviour (only for repositories set up at `0.5.0` or later). In `docs/plan/direction.md`, record that tickets-only is Chitty's original purpose and the runner an optional layer.
- Out of scope: `chitty init` (its config template still writes `review = true`; TASK-331 changes it), the managed block, and hiding commands or guides.
- Tests: Hypothesis is the property-testing tool; put them in `tests/test_config_workflow.py`.

## Acceptance Criteria

- [ ] Property: for any version string of one to four dot-separated non-negative integers, and for `None`, `resolve_workflow(None, v)` is `"runner"` exactly when `v` is `None` or `version_key(v) < version_key("0.5.0")`, else `"tickets"`; and for either explicit value `w`, `resolve_workflow(w, v) == w`. Fails today because the function does not exist.
- [ ] Loading a temp repository config: no `workflow` with `chitty_version = "0.4.2"`, with `"0.5.0"`, and with no `chitty_version` gives `config.workflow` of `runner`, `tickets` and `runner`; `workflow = "bogus"` and `workflow = 1` fail with an error naming `workflow`, `tickets` and `runner`.
- [ ] For every combination of workflow (`tickets`, `runner`), repository `review` (unset, `true`, `false`) and context `review` (unset, `true`, `false`), `Repo.review_required` returns the context value if set, else the repository value if set, else `false` under `tickets` and `true` under `runner`. A small fixed set of 18 cases, each tested, so no property is needed. The `tickets` with both unset case fails today.
- [ ] `docs/plan/config.md` documents `workflow`, `FIRST_WORKFLOW_VERSION` and the changed-default decision; `docs/plan/direction.md` records that tickets-only is the original purpose; `make check` passes.

## Notes

Replanned with the human on 2026-11-14. The original ask (agents feel they must write tickets for a weaker agent and cannot review their own) is solved by a tickets-only workflow chosen at install time, not by an exploratory agent mode. Stages: this ticket (setting), then `chitty init` with migration, then the managed block, hidden runner commands and hidden role guides. Earlier cold-read questions about `chitty run` invocation no longer apply.

## History

- 2026-11-14T13:39:35Z jolly-umber-badger → planning
- 2026-11-14T13:40:56Z jolly-umber-badger: changed notes
- 2026-11-14T18:21:52Z friendly-ginger-adder: replaced notes; changed title, labels, description, acceptance criteria
- 2026-11-14T18:23:25Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:28:28Z friendly-ginger-adder: changed title, description, acceptance criteria
- 2026-11-14T18:28:41Z friendly-ginger-adder: changed owner
- 2026-11-14T18:28:41Z friendly-ginger-adder planning → cold-read
