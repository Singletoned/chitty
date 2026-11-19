---
title: Add the optional `rebase_model` setting for rebase sessions
status: done
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

- [x] `_model_arguments` called with mode `rebase` returns `("--model", <value>)` when `rebase_model` is set and `()` when unset or when the command already has `--model`; modes `work` and `review` behave as before
- [x] [x] `chitty init` in a new repository writes the commented `rebase_model` line directly after `review_model`; upgrading an existing config adds it once, with the other missing settings, as for `work_model`, and the result parses as TOML; a second `chitty init` does not add it again; `rebase_model = "  "` makes `Repo.open` raise `ChittyError` naming `rebase_model`; `_model_arguments` with mode `other` raises `ChittyError` naming it
- [x] `docs/plan/config.md` and `docs/plan/next-action-and-runner.md` mention `rebase_model`; `make check` passes

## Plan

Add optional rebase_model to configuration validation and both generated templates. Make _model_arguments select an explicit model setting from its mode and reject unknown modes; update its caller. Cover set/unset/model-override and invalid mode, config validation, plus init insertion/idempotence in model-default tests. Document the setting and run focused tests followed by make format and make check.

## Notes

Review failed (tests): Newly discovered upgrade case: insert the new comment immediately after the existing review_model line and add a regression test for upgrading an existing configuration; the current test checks only relative order. No earlier review notes exist.
1: pass - `make check` printed `Ran 677 tests` and `OK`; the mode-selection test covers set, unset and explicit model override.
2: fail - Created a repository with `chitty init`, removed only the new comment, then ran `chitty init` again: both commands exited 0, but review_model was on line 12 and rebase_model on line 15, not directly after it. Existing init test checks less-than rather than adjacency. Blank validation and unknown mode are exercised by `make check`.
3: pass - Both plan documents mention rebase_model; `make check` printed `Ran 677 tests` and `OK`.

Implementation attempt: added an upgrade adjacency regression test (confirmed it fails before the change) and adjusted init insertion. The focused test still fails: upgrade does not insert the comment adjacent to the active review_model line. Root cause remains unresolved; no full check run. Preserve this partial work for follow-up.

Resolved the upgrade adjacency case: init now inserts the missing rebase_model comment immediately after the active review_model line and adjusts the subsequent insertion offset. The focused model-default tests pass, including repeated init idempotence and pyproject configuration. Verification: make check (678 tests, OK); make format; chitty fix on the ticket file (warning only for existing plan markdown). The earlier failing-test note records the pre-fix discovery.

Review failed (tests): Newly discovered configuration corruption in init; restrict review_model lookup and insertion offset to the Chitty section and add regression coverage for other TOML tables. The earlier adjacency failure in the previous review note is resolved by the upgrade regression test.
1: pass - make check printed Ran 678 tests and OK; mode selection test exercises set, unset rebase and explicit override.
2: fail - Running _add_missing_settings on a pyproject with a commented review_model in [tool.chitty] and an active review_model in [tool.other] inserted rebase_model in the other table and split its comment with other additions; tomllib.loads printed TOMLDecodeError Expected equals after a key. The prior upgrade adjacency test was reported failing before the fix in the implementation attempt note and now passes in make check. Blank validation and unknown mode also pass in make check.
3: pass - Both plan documents mention rebase_model; make check printed Ran 678 tests and OK.

Review follow-up: scoped review_model adjacency lookup to the [tool.chitty] section, preventing a review_model in another pyproject table from being used as the insertion point and corrupting TOML. Added regression coverage preserving [tool.other]. Focused model-default tests pass (9 tests); make check passes (679 tests). make format run; chitty fix reports existing Markdown underscore warnings.

Review failed (tests): Newly discovered missing final newline case: ensure insertion starts on a new line and add regression coverage, including repeated init. The earlier adjacency and other-table corruption findings are resolved for their reported inputs; the prior notes document their pre-fix failures.
1: pass - `make check` printed `Ran 679 tests` and `OK`; mode tests exercise configured models, unset rebase and explicit override.
2: fail - Running `_add_missing_settings` with valid TOML `review_model = "some/model"` without a final newline printed `review_model = "some/model"# rebase_model = ...`, placing the comment on the same line rather than directly after it. Add a newline before the inserted comment. Existing tests cover blank models and unknown modes; the prior implementation note records the adjacency regression failing before its fix, and the preceding review note records the other-table corruption reproduction.
3: pass - Both plan documents mention `rebase_model`; `make check` printed `Ran 679 tests` and `OK`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Planning decision 2026-11-19, with the owner, after three failed reviews: "directly after `review_model`" applies to a fresh `chitty init` only. An upgrade adds `rebase_model` in the block of missing settings, exactly as `work_model` is added today; placing settings neatly in an existing file is a separate job (a config reformat, its own ticket). Criterion 2 reworded to say so. Reverted the splice in `_add_missing_settings` (`src/chitty/store.py` now differs from `main` only by the `rebase_model` entry and its key in the set) and replaced the upgrade-adjacency test with `test_init_adds_rebase_model_once_when_upgrading`, which runs `init` twice and checks one line and valid TOML. The other-table test stays. `make check` passes.

Reviewed: Previous upgrade adjacency and missing-newline findings were superseded by the documented planning decision; the other-table corruption regression is covered.
1: pass - `make check` printed `Ran 686 tests` and `OK`; model selection tests exercise configured modes, unset rebase and explicit override.
2: pass - `make check` printed `Ran 686 tests` and `OK`, including upgrade idempotence, TOML parsing, other-table preservation, blank validation and unknown mode; inspecting `INITIAL_CONFIG` printed the rebase comment immediately after review_model.
3: pass - Both plan documents mention rebase_model and its use; `make check` printed `Ran 686 tests` and `OK`.

## Summary

Implemented optional rebase_model and fixed init upgrade insertion to stay within the Chitty configuration table. Added regression coverage for another pyproject table containing review_model. Verification: focused model-default tests (9 pass), make format, make check (679 tests pass), and chitty fix (existing Markdown warnings only). Commit: 51a62c77. No follow-ups.

## History

- 2026-11-18T18:17:25Z lively-quartz-crane → backlog
- 2026-11-18T18:17:46Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:17:46Z lively-quartz-crane backlog → cold-read
- 2026-11-18T18:19:11Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:19:11Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:19:13Z lively-quartz-crane planning → todo
- 2026-11-18T23:20:15Z plucky-bronze-jay todo → doing
- 2026-11-18T23:21:07Z plucky-bronze-jay: wrote the plan
- 2026-11-18T23:23:10Z plucky-bronze-jay: changed summary; ticked acceptance criteria
- 2026-11-18T23:23:10Z plucky-bronze-jay doing → review
- 2026-11-18T23:25:53Z open-ochre-marten: changed acceptance criteria, notes
- 2026-11-18T23:25:53Z open-ochre-marten review → doing
- 2026-11-18T23:29:18Z able-coral-zander: changed notes
- 2026-11-18T23:33:58Z able-coral-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-18T23:33:58Z able-coral-zander doing → review
- 2026-11-18T23:35:34Z able-lilac-yellowhammer: changed acceptance criteria, notes
- 2026-11-18T23:35:34Z able-lilac-yellowhammer review → doing
- 2026-11-18T23:38:58Z intrepid-violet-lapwing: changed notes, summary
- 2026-11-18T23:38:58Z intrepid-violet-lapwing doing → review
- 2026-11-18T23:41:16Z witty-coral-gannet: changed owner, acceptance criteria, notes
- 2026-11-18T23:41:16Z witty-coral-gannet review → blocked
- 2026-11-19T10:00:28Z quick-ginger-lapwing: changed owner, acceptance criteria, notes
- 2026-11-19T10:00:28Z quick-ginger-lapwing blocked → review
- 2026-11-19T10:00:39Z quick-ginger-lapwing: ticked acceptance criteria
- 2026-11-19T10:32:35Z witty-coral-gannet: changed notes
- 2026-11-19T10:32:35Z witty-coral-gannet review → done
