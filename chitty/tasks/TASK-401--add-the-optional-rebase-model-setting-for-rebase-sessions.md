---
title: Add the optional `rebase_model` setting for rebase sessions
status: todo
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-375` runs a separate, cheap agent session to resolve rebase conflicts before a review, so that conflict context never mixes with review context. It should be able to use a cheaper model than the reviewer. Add the setting on its own, ahead of the session.

Decisions:

- New optional setting `rebase_model`, handled like `work_model` and `review_model`: the field and its validator in `src/chitty/config.py` (the field list around line 96 and the `field_validator` around line 142), the commented template line in `config.py` directly after the `review_model` line (`# rebase_model = "provider/model" # default for rebase sessions when the command has no model`), and both places in the `chitty init` template in `src/chitty/store.py` (the additions tuple around line 1146, directly after `review_model`, with `# rebase_model = "provider/model" # default for rebase sessions` and the `{\"work_model\", \"review_model\"}` set beside it).
- `_model_arguments` in `src/chitty/run.py` takes the session mode (`\"work\"`, `\"review\"` or `\"rebase\"`) as a new `mode: str` argument instead of reading `action.mode`, and picks `work_model`, `review_model` or `rebase_model` by it; any other mode raises `ChittyError` naming the mode. Its one caller passes `action.mode` for now (`NextAction.mode` cannot be `rebase` yet, so tests call `_model_arguments` directly). Unset means no `--model`, as for the other modes.
- Document `rebase_model` and its unset behaviour in `docs/plan/config.md`, and add it to the sentence in `docs/plan/next-action-and-runner.md` (around line 67) saying `work_model` and `review_model` add `--model`.

Tests: in `tests/test_run_model_defaults.py`, which tests the existing model settings. No property: three modes by set or unset, each tested.

## Acceptance Criteria

- [ ] `_model_arguments` called with mode `rebase` returns `("--model", <value>)` when `rebase_model` is set and `()` when unset or when the command already has `--model`; modes `work` and `review` behave as before
- [ ] `chitty init` writes the commented `rebase_model` line directly after `review_model`, and a second `chitty init` does not add it again (a new test in `tests/test_run_model_defaults.py` or beside the existing init tests); `rebase_model = "  "` makes `Repo.open` raise `ChittyError` naming `rebase_model`; `_model_arguments` with mode `other` raises `ChittyError` naming it
- [ ] `docs/plan/config.md` and `docs/plan/next-action-and-runner.md` mention `rebase_model`; `make check` passes

## History

- 2026-11-18T18:17:25Z lively-quartz-crane → backlog
- 2026-11-18T18:17:46Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:17:46Z lively-quartz-crane backlog → cold-read
- 2026-11-18T18:19:11Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:19:11Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:19:13Z lively-quartz-crane planning → todo
