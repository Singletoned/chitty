---
title: Read a ticket from the current branch when that branch changed it
status: todo
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: Chitty, and cold readers, should read tickets from the branch they are on. This is needed for planning on a branch (`TASK-340`): a planner working in a worktree on a planning branch must see, and be able to edit, the tickets as that branch has them.

Today `ticket_source` (`src/chitty/ticket_source.py`) looks only at `main` and the ticket's own `task-<n>` branch (and its remote-tracking refs). On any other branch, with no ticket branch ahead of `main`, it returns `main`: a planner on a branch reads `main`'s copy of a ticket, not the branch's, even after editing it there.

Decisions, for a checkout on a branch `B` that is neither the configured main branch nor the ticket's own branch (`str(task_id).lower()`), and only when `main` has a tip (with no tip, today's behaviour applies, including the `configured main branch ... has no tip` error). The checks compare commits only; that is enough because Chitty commits every write it makes, so an uncommitted hand edit on `B` is not seen, as today:

- Paths: the ticket's files in `B`'s working tree (`Repo._working_ticket_files`) together with its files on `main` (`Repo._ref_ticket_files(main_ref, task_id)`), so a ticket `B` added or renamed is included.
- `current_changed`: `git.changed_since_split(root, "HEAD", main_ref, paths)` (`B` changed the ticket since it split from `main`). `main_changed`: `git.changed_since_split(root, main_ref, "HEAD", paths)`. Both are computed only in this case; elsewhere they are `False`.
- `ticket_source` gains two keyword-only parameters after `changed_on_both`, `current_changed: bool` and `main_changed: bool`; `changed_on_both` stays as it is (it compares a ticket branch with `main`). With `K` meaning "a ticket-branch candidate not contained in `main` exists" (today's `candidates` after filtering), the result for such a `B` is:

  | `current_changed` | `main_changed` | `K` | result |
  |---|---|---|---|
  | yes | no | no | `WORKING_TREE` |
  | yes | yes | no | raise `ticket <id> changed on both <B> and <main>; rebase <B> onto <main>` |
  | yes | either | yes | raise `ticket <id> changed on both <B> and <ref>`, where `<ref>` is the short name today's logic would choose (for example `task-3` or `origin/task-3`) |
  | no | no | no | `WORKING_TREE` (the copies are the same; edits then go to `B`) |
  | no | yes | no | today's logic: `main` |
  | no | either | yes | today's logic: the ticket branch wins |

  Ids and branch names in the messages are in backticks, as the existing `changed on both` message has them. A fresh `B` with no commits since the split, or one behind `main` that has not touched the ticket, falls in the `no` rows.
- On `main` itself, on the ticket's own branch, and on a detached `HEAD` (`current_branch` is `None`), nothing changes.
- In the `K` rows with `current_changed` yes, the `<B>` message is raised first, before today's `changed_on_both` check on the ticket branch.
- Writes follow the chosen source, as today: when the source is `WORKING_TREE`, `chitty edit` on `B` writes and commits there.

Out of scope: landing a planning branch (`TASK-340`), and the cold-read guide's wording (it already tells readers to run `chitty show`; they get this for free when started in the planner's worktree).

Tests:

- Pure, in `tests/test_property_ticket_source.py`: extend the existing strategies so a drawn case can have a current branch that is neither main nor the ticket branch, both booleans drawn, and with and without a ticket-branch candidate ahead of `main` (draw the three facts as one value from `st.sampled_from` of the eight combinations, so every row is reachable, and also enumerate the eight combinations in a plain loop (or `subTest`s) with fixed graphs, so every row is checked whatever the Hypothesis profile; the existing positional `call()` helper must pass the two new booleans). Assert the table above, and that the result equals today's whenever `current_branch` is main or the ticket branch, whatever the booleans.
- Real Git, in a new `tests/test_source_current_branch.py` with `RepoTestCase`: a repository with `TASK-1` and `TASK-2` committed on `main`; a branch `plan-a` in a linked worktree. (a) On `plan-a`, `chitty edit TASK-1 --title "Branch title"`; then `chitty show TASK-1` in that worktree prints `Branch title`, and in the main checkout prints the old title. (b) Commit a change to `TASK-2` on `main`; `chitty show TASK-2` in the `plan-a` worktree prints `main`'s new copy. (c) Then change `TASK-2` on `plan-a` too (commit with `git` directly; `TASK-2` has no ticket branch): `chitty show TASK-2` there fails with the `main` both-changed message. (e) A fresh branch `plan-b` from `main` with no commits: `chitty show TASK-1` there prints `main`'s copy (this half passes today too), and `chitty edit TASK-1 --title X` there exits 0 and makes a commit on `plan-b` that changes `TASK-1`'s file (this half fails today; record the failure). (d) `TASK-3` with a `task-3` branch ahead of `main`: on `plan-a`, `chitty show TASK-3` gives the `task-3` copy. (f) Then change `TASK-3` on `plan-a` too (commit with `git` directly): `chitty show TASK-3` there fails with the `changed on both` message naming `plan-a` and `task-3`.

## Acceptance Criteria

- [ ] The extended property, the eight-row enumeration and the six real-Git cases pass; before the change the property, the enumeration, the edit and show steps of (a), cases (c) and (f), and the edit step of (e) fail; record both runs in a note
- [ ] All existing `ticket_source` and source-copy tests pass unchanged; `make check` passes

## History

- 2026-11-22T22:51:27Z plucky-umber-wren → cold-read
- 2026-11-22T22:53:28Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:56:25Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:57:16Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:57:16Z plucky-umber-wren cold-read → todo
