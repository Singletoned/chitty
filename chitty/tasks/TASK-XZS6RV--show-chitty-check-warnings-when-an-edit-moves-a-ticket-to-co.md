---
title: Show `chitty check` warnings when an edit moves a ticket to `cold-read` or `todo`
status: cold-read
created: 2026-11-26
provisional: true
---

## Description

### Why

On 2026-11-25 a planner scripted `chitty edit TASK-472 -s planning --replace-in-description ...`, then `chitty check <file>`, then `chitty edit TASK-472 -s todo`. The first edit was refused, but the script went on and moved the ticket to `todo` without its fixes. The plan guide makes `chitty check` a separate step ("run `chitty check` on the ticket file before starting a reader"), so planners script the sequence as separate commands. Decided (the person, 2026-11-26): the move itself runs the ticket's checks, so the separate step goes. The plan guide's line on joining commands with `&&` is TASK-HR7PKP.

Today `Repo._commit` (`src/chitty/store.py`) already runs `check.fix` on the written task files and refuses on errors, but only when `autoformat` or `autocommit` is set, and it discards the warnings.

### Change

- In `Repo._commit`, also run that validation when the change moves a ticket into `cold-read` or `todo` (`change.previous_status` differs from the new status, which is one of those two). For such a move, put the warnings (problems that are not errors) on the result as a new `Change` field `warnings: tuple[str, ...]`, each `str(problem)`, in the order `fix` returns them. Other writes keep `warnings` empty.
- In `src/chitty/check.py`, include `cold-read` in the statuses that get the acceptance-criteria and specification-length warnings, so a planner sees them before a reader starts.
- `edit` in `src/chitty/cli.py` prints each warning on its own line after the `updated ...` line (not with `--json`). `edit` in `src/chitty/mcp.py` adds `"warnings": [...]` to its result when there are any.
- In `src/chitty/roles/plan.md`, replace "and run `chitty check` on the ticket file before starting a reader" with "; moving a ticket to `cold-read` or `todo` shows its `chitty check` warnings". The guide gets a few words shorter.

### Out of scope

Running the configured repository check; warnings for other statuses or other commands; the MCP branch warnings of TASK-10034.

## Acceptance Criteria

- [ ] In a new `tests/test_edit_warnings.py` (`RepoTestCase`, default config with `autocommit = false`), a ticket with 6 acceptance criteria is moved with `chitty edit <ID> -s cold-read`, then `-s planning`, then `-s todo`, through the CLI runner. The `cold-read` and `todo` moves exit 0 and print a line containing `warning: 6 acceptance criteria`; the `planning` move does not. Through `mcp.edit(id, status="todo")` on the same ticket after moving it back to `planning`, the result has `warnings` containing that message, and an edit that does not move the ticket into `cold-read` or `todo` has no `warnings` key. Fails without the change.
- [ ] A ticket whose `depends_on` names a missing ticket is refused by `chitty edit <ID> -s todo` with `autocommit = false`, the output names the problem, and the file still has its old status. Fails without the change. Regression tests: `TestTicketSizeWarnings.test_limits` passes with its expected warning statuses updated to include `cold-read`. `make check` passes.

## History

- 2026-11-26T10:54:53Z calm-ochre-quail → backlog
- 2026-11-26T10:54:57Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:16Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:16Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:15:34Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:15:34Z calm-ochre-quail to-plan → cold-read
