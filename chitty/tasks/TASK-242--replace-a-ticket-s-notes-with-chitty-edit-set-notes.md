---
title: Replace a ticket's notes with `chitty edit --set-notes`
status: doing
created: 2026-11-10
---

## Description

Notes are append-only through the CLI and MCP, so collapsing a ticket's cold-read history meant hand-editing task files. In mullion, notes reached 4,000 to 6,000 characters per ticket, full of reversed decisions and deleted refs that workers can mistake for instructions.

Decisions:

- Add `chitty edit ID --set-notes TEXT` and `--set-notes-file F` (`-` for stdin), which replace the whole Notes section; `''` removes it. They mirror `--plan` / `--plan-file`. They cannot be combined with `--note` or `--note-file` in one edit. Record `replaced notes` in History.
- `--set-notes` does not count as the note that `blocked`, `review → doing` and `review → done` require; those still need `--note`. It is rejected while a task is in review, as criteria edits are (`check_edit` in `src/chitty/store.py`), so review evidence cannot be replaced mid-review. `--set-notes ''` with no Notes section is a no-op.
- Add the field to `Edit` in `src/chitty/store.py` (the existing `notes` field is the list to append, so name it `set_notes`) and expose it as a `set_notes` parameter of the MCP `edit` tool in `src/chitty/mcp.py`.
- In `src/chitty/roles/plan.md`, add one line: once a ticket's reads converge, replace its notes with only what the worker and reviewer need (verified facts, and the mutant list as a reviewer checklist); outcomes stay in git history.
- Update the Notes and CLI sections of `PLAN.md`. Put the guide test in a new `tests/test_guide_set_notes.py`.

## Acceptance Criteria

- [ ] A test sets two notes, runs `chitty edit ID --set-notes TEXT`, and `chitty show` has exactly TEXT as Notes; with `--set-notes ''` the Notes section is gone; History records `replaced notes`.
- [ ] Tests show `--set-notes` combined with `--note` fails, and `--set-notes` on a task in review fails; neither changes the file.
- [ ] A test in `tests/test_mcp.py` replaces notes through the MCP `edit` tool with `set_notes`.
- [ ] `guide("plan")` tells planners to replace converged notes with only verified facts and the reviewer checklist.

## Plan

Add `set_notes` to `Edit`, with replacement/removal semantics and a History entry in the store edit path. Enforce incompatibility with append-note inputs and reject replacement during review, while preserving required transition-note validation. Expose `--set-notes` and `--set-notes-file` in CLI and `set_notes` in MCP. Update the plan role guide and the Notes/CLI sections in `PLAN.md`. Add focused store/CLI and MCP tests plus a separate `tests/test_guide_set_notes.py`; run the regression tests before the implementation to confirm failure, then format and check.

## Notes

Cold read 1 (Haiku): decided: `--set-notes` does not satisfy required status-change notes and is rejected in review, so review evidence stays. Stated: guide test file, no-op on absent Notes. Accepted: four criteria is within the limit. Possible starting point: `git diff main...refs/cold-read/TASK-242/1`; check it against the current criteria, not trust it; it lacks the in-review rejection.

## History

- 2026-11-10T14:08:42Z jolly-heron → backlog
- 2026-11-10T14:19:52Z jolly-heron: changed description, acceptance criteria, notes
- 2026-11-10T14:19:53Z jolly-heron backlog → todo
- 2026-11-10T17:10:35Z mellow-newt todo → doing
- 2026-11-10T17:10:49Z mellow-newt: wrote the plan
