---
title: Read a provisional ticket from its own branch when that branch is ahead of main
status: planning
labels:
  - bug
priority: high
created: 2026-11-24
---

## Description

A ticket with a provisional ID is always read from the working tree, even when its own `task-<id>` branch is ahead of `main`. So the main checkout (`chitty show`, `chitty list`, runner selection) never sees status changes made on that branch.

Seen twice:

- 2026-11-23 21:01: `TASK-YJ6VBS` was `todo` on `main` and `review` on `task-yj6vbs`. Selection picked it for work, the claim read the branch copy and refused, and `chitty run --loop --mode work` stopped with `Error: moving review → doing requires --note with the reason` (log `.git/chitty/run/TASK-YJ6VBS-20261123210202964248Z.log`).
- 2026-11-24 09:39 to 16:06: `TASK-FER4EB` was `todo` on `main`. Each worker set it to `planning` on `task-fer4eb`, `main` still showed `todo`, and the runner picked it again: about 70 work sessions. On 2026-11-24 its `main` copy was set to `planning` by hand to stop the loop.

Cause: `ticket_source` in `src/chitty/ticket_source.py` starts with `if provisional: return WORKING_TREE`. `Repo._choose_source` (`src/chitty/store.py`) passes `provisional` as true for any ID with a non-numeric number whose file is in the working tree or on `main`. That early return exists for a ticket created with a provisional ID on some other branch: it exists only in that working tree, and the normal rules would read `main`, where it is absent (`tests/test_source_copy.py::TestSourceCopy::test_provisional_is_read_from_the_id` covers this). It wrongly also skips the ticket's own branch.

Change, in `ticket_source` only: delete the early return, and in the branch `if not candidates:` (after candidates that `main` contains are dropped) return `WORKING_TREE` first when `provisional` is true, before the `current_branch == main_branch` and missing-main-tip checks. A provisional ticket with a surviving candidate then follows the same rules as any other ticket. Update the docstring or comments that describe the old rule. `src/chitty/store.py` does not change.

Out of scope: refusing to run or land an unrenumbered provisional ticket, and making a claim that finds the branch copy past `doing` skip the ticket instead of stopping the loop. Both were suggested in this ticket's earlier text; neither is needed once the branch copy is read.

Tests:

- In `tests/test_property_ticket_source.py`, replace `test_rule_1_provisional_reads_the_working_tree` with `test_rule_1_provisional_follows_the_other_rules_unless_none_apply`, drawing inputs exactly as the old test does. Compute the outcome for `provisional=False` and for `provisional=True`, each as `("value", result)` or `("error", message)`, as `test_decoys_and_unrelated_refs_do_not_change_generated_result` does. If the non-provisional outcome is `("value", main_branch)`, or an error whose message contains `has no tip`, assert the provisional outcome is `("value", WORKING_TREE)`. Otherwise assert the two outcomes are equal. This works because `main_branch` and the missing-tip error come only from the no-candidates path, which is the one place the two differ.
- In `tests/test_source_copy.py`, add `test_provisional_on_main_with_its_own_branch_ahead_is_read_from_it` to `TestSourceCopy`. `init_git`; write `self.file("K7Q2MY")` with `provisional: true` added as `test_provisional_only_on_its_branch_is_read_from_it` does, and `commit`; `git checkout -b task-k7q2my`; write it again with title `branch`, still with `provisional: true`, and `commit`; `git checkout main`. Assert `self.source("K7Q2MY")` with `assert_copy` is ref `task-k7q2my`, path `chitty/tasks/TASK-K7Q2MY--example.md`, title `branch`. Then `git merge --ff-only task-k7q2my`, and assert the copy is ref `None` with title `branch`.

Both new tests fail on `main` today. The existing `test_provisional_is_read_from_the_id`, `test_provisional_only_on_its_branch_is_read_from_it` and `test_provisional_in_linked_worktree` must keep passing unchanged.

## Acceptance Criteria

- [ ] The new property test `test_rule_1_provisional_follows_the_other_rules_unless_none_apply` and `test_provisional_on_main_with_its_own_branch_ahead_is_read_from_it` pass, and each fails on `main`; a note records both runs. Regression tests: `test_provisional_is_read_from_the_id`, `test_provisional_only_on_its_branch_is_read_from_it`, `test_provisional_in_linked_worktree`
- [ ] `make check` passes

## Notes

Suggestion origin: chitty

Planner, 2026-11-25: probed on a trial patch of `main` (the change and both tests as described). Before the change both new tests fail; after it, `tests/test_property_ticket_source.py` and `tests/test_source_copy.py` pass (23 tests), including the three regression tests. No other test changed result.

## History

- 2026-11-24T22:21:27Z zesty-coral-newt → backlog
- 2026-11-24T22:21:28Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:40Z zesty-coral-newt: changed labels
- 2026-11-24T22:40:53Z zesty-coral-newt: changed priority
- 2026-11-25T10:27:18Z sunny-hazel-gannet: changed title, description, acceptance criteria
- 2026-11-25T10:27:18Z sunny-hazel-gannet backlog → planning
- 2026-11-25T10:32:14Z sunny-hazel-gannet: changed notes
