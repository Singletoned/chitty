---
title: Show `chitty check` warnings when an edit moves a ticket to `cold-read` or `todo`
status: done
created: 2026-11-26
moved_from: TASK-XZS6RV
---

## Description

### Why

On 2026-11-25 a planner scripted an edit, then `chitty check <file>`, then `chitty edit TASK-472 -s todo`; the first edit was refused, but the last still moved the ticket to `todo` without its fixes. The plan guide makes `chitty check` a separate step. Decided (the person, 2026-11-26): the move itself runs the ticket's checks, so that step goes.

Today `Repo._commit` (`src/chitty/store.py`) already runs `check.fix` on the written task files and refuses on errors, but only when `autoformat` or `autocommit` is set, and it discards the warnings.

### Change

- In `Repo._commit`, a change is a checked move when `change.previous_status is not None` (only `_edit_stored` sets it; `add`, `archive`, `move` and `renumber` leave it `None`) and differs from the new status, which is `cold-read` or `todo`. For a checked move, get the problems for the written task files from `check(self, self.contexts(), task_paths, include_worktree_state=False)`, which has no side effects, even when the `fix` call also runs: `fix` skips a ticket whose source is another ref (it warned `skipped: read from main` for a numbered ticket edited on a `plan/` branch on 2026-11-26), and those are the edits that most need checking. Refuse on errors with the same message as today. Put the warnings (problems that are not errors) on the result as a new `Change` field `warnings: tuple[str, ...]`, each `str(problem)`, in the order returned. Other writes keep `warnings` empty.
- In `src/chitty/check.py`, include `cold-read` in the statuses that get the acceptance-criteria and specification-length warnings, so a planner sees them before a reader starts.
- `edit` in `src/chitty/cli.py` prints each warning on its own line after the `updated ...` line (not with `--json`). `edit` in `src/chitty/mcp.py` adds `"warnings": [...]` to its result when there are any.
- In `src/chitty/roles/plan.md`, replace "and run `chitty check` on the ticket file before starting a reader" with "; moving a ticket to `cold-read` or `todo` shows its `chitty check` warnings". The guide gets a few words shorter.

### Out of scope

Running the configured repository check; warnings for other statuses or other commands; the MCP branch warnings of TASK-10034.

## Acceptance Criteria

- [x] In a new `tests/test_edit_warnings.py` (`RepoTestCase`, default config with `autocommit = false`), a ticket in `planning` with 6 acceptance criteria is moved with `chitty edit <ID> -s cold-read`, then `-s planning`, then `-s todo`, through the CLI runner. The `cold-read` and `todo` moves exit 0 and print a line containing `warning: 6 acceptance criteria`; the `planning` move does not, and `chitty add` of a 6-criterion ticket with `-s todo` prints no warning. Through `mcp.edit(id, status="todo")` on the same ticket after moving it back to `planning`, the result has `warnings` containing that message, and an edit that does not move the ticket into `cold-read` or `todo` has no `warnings` key. Fails without the change.
- [x] A `planning` ticket whose `depends_on` names a missing ticket (written into the file directly, as `test_limits` writes History, since `chitty add` and `chitty edit --depends-on` refuse it) is refused by `chitty edit <ID> -s todo` with `autocommit = false`; the output names the problem, and the file still has `status: planning`. Fails without the change. Regression tests: `TestTicketSizeWarnings.test_limits` passes with its expected warning statuses updated to include `cold-read`. `make check` passes.

## Plan

Add failing CLI and MCP coverage for checked status moves, then propagate check warnings and errors through the store and front ends, update the guide and status regression test, and run formatting and checks.

## Notes

Before the fix, both new tests fail: checked moves omit warnings and accept a missing dependency.

Reviewed: complete diff inspected; checks passed.
1: pass - `make check` passes the CLI and MCP transition tests; applying `tests/test_edit_warnings.py` to the merge base and running `python -m pytest tests/test_edit_warnings.py -q` fails because the cold-read warning is absent.
2: pass - `make check` passes, including `TestTicketSizeWarnings.test_limits`; the same merge-base test run fails because the missing-dependency edit exits 0 instead of 1.

## Summary

Checked moves to cold-read or todo now refuse errors and surface warnings in CLI and MCP; updated planning guidance and regression coverage. make check passed. Both new tests failed before the fix.

## History

- 2026-11-26T10:54:53Z calm-ochre-quail → backlog
- 2026-11-26T10:54:57Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:16Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:16Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:15:34Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:15:34Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:17:06Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T11:17:06Z calm-ochre-quail cold-read → todo
- 2026-11-26T11:17:24Z calm-ochre-quail: changed description
- 2026-11-26T15:26:07Z rosy-pearl-toad todo → doing
- 2026-11-26T15:30:03Z rosy-pearl-toad: wrote the plan
- 2026-11-26T15:30:45Z rosy-pearl-toad: changed notes
- 2026-11-26T15:39:40Z rosy-pearl-toad: changed summary
- 2026-11-26T15:42:08Z rosy-pearl-toad doing → review
- 2026-11-26T15:48:11Z sunny-maroon-crane: changed notes; ticked acceptance criteria
- 2026-11-26T15:48:11Z sunny-maroon-crane review → done
- 2026-11-26T17:47:31Z calm-ochre-quail: changed description
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-XZS6RV
