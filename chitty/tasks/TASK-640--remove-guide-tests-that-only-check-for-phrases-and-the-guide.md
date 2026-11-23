---
title: Remove guide tests that only check for phrases, and the guide word budgets
status: planning
depends_on:
  - TASK-615
created: 2026-11-23
---

## Description

Many guide tests only check that a phrase is, or is not, in a guide or prompt. They show that a worker typed the requested words, not that agents behave differently, and every rewording has to reword them too. `tests/test_guide_word_budget.py` caps each guide's word count with numbers that can be raised by a one-line edit. It also leaves out `src/chitty/guide-runner.md`, the block every repository's `AGENTS.md` gets. Decision (the person, 2026-11-23): remove both. Length is weighed by planners and reviewers instead (separate ticket).

Rule: remove a test whose assertions are only phrase checks (`assertIn`, `assertNotIn`, `assertRegex` or `assertNotRegex` on text) on `src/chitty/guide.md`, `src/chitty/guide-runner.md`, a file in `src/chitty/roles/`, `guide()` output, or `continuation_prompt()` in `src/chitty/run.py`. Keep tests that exercise code: rendering, composition, the ticket-ID prefix, `<!-- property-signals -->` insertion, refusals, `chitty init` upgrades, rebase-text injection, Pi warnings, and rules checked over all guide text (no ticket IDs, no language names).

Delete these files under `tests/`, all `test_guide_*.py`:
`backticks`, `cold_read_mutants`, `cold_read_notes`, `cold_read_reports`, `cold_read_sufficiency`, `plan`, `plan_convergence`, `plan_dependency_reread`, `planner_evidence`, `read_only_cold_read`, `repair_missing_branch`, `return_scope`, `return_to_planning`, `review_cleanliness`, `review_completeness`, `setup_validation`, `work_commits`, `worktree_boundary`, `word_budget`.

These lists are the complete set: if you find another test that seems to match the rule, note it instead of removing it.

In files that are kept, remove only these tests:
- `tests/test_guide_cold_read.py`: `test_prints_the_reader_procedure`, `test_plan_guide_points_at_the_reader_guide`.
- `tests/test_guide_plan_restored.py`: class `TestPlanGuideRestored`, and `test_cold_read_guide_addresses_only_the_reader`.
- `tests/test_guide_property_tests.py`: `test_planning_guide_specifies_properties`, `test_cold_read_guide_reports_missed_properties`. The marker replacement they also check is covered by `assert_compatibility` in `tests/test_guide_workflow.py`.
- `tests/test_guide_review_evidence.py`: `test_review_guide_requires_evidence_for_failures`.
- `tests/test_guide_setup.py`: in `test_setup_guide_works_without_a_repository`, remove the phrase loop and keep the exit-code check.
- `tests/test_cli.py`, class `TestGuide`: `test_plan_guide_describes_read_only_cold_reads`, `test_plan_guide_requires_decision_tests_and_expected_route`, `test_work_guide_requires_regression_test_failure_and_wrong_ticket_stop`, `test_branch_discoveries_use_provisional_ids_in_sequential_contexts`, `test_worker_guides_start_with_show_without_pulling_inbox`, `test_guide_points_agents_at_ticket_planning_instructions`.
- `tests/test_statuses_planning.py`: `test_plan_guide_names_both_statuses`.

Remove imports and helpers left unused. Keep everything else, including `tests/test_guide_workflow_block.py` and its snapshot `tests/fixtures/guide-runner-expected.md`, which test how the block is built and upgraded.

Also:
- `AGENTS.md` (outside the managed block): replace the bullet starting "Put a ticket's new guide tests in their own file" with: do not add tests that only check that a guide or prompt contains a phrase; test the code that builds or serves guides instead.
- `docs/plan/agent-instructions.md`: record the decision and the reason in one bullet.

Out of scope: phrase checks on `README.md` or `docs/` (such as `test_docs_list_both_statuses` and `test_readme_review_example_uses_a_real_newline`, which stay); any change to guide text.

No property: this change only removes tests. What remains is covered by the kept tests named above.

## Acceptance Criteria

- [ ] The tests `pytest --collect-only -q tests/` collects on the branch are exactly those it collects on `main` minus the files and tests this ticket lists; record both commands and the difference in a note.
- [ ] `make check` passes.

## History

- 2026-11-23T12:34:45Z friendly-zinc-dormouse → planning
