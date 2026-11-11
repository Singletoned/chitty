---
title: Add planning and cold-read statuses
status: done
labels:
  - plan-next
  - needs-minor
created: 2026-11-11
---

## Description

Add two statuses so ticket writing is visible: `planning` (a ticket being written) and `cold-read` (waiting for a cold read).

- Flow: `backlog` → `planning` → `cold-read` → `planning` → `todo` → `review` → `done`. `doing` and `blocked` are unchanged.
- `STATUSES` in `src/chitty/model.py` becomes `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `review`, `done`. Glyphs and labels: `📝 plan`, `🔎 cold`. Also update the `Literal` types in `model.py` and `src/chitty/mcp.py`.
- `chitty list` and MCP list without a status filter show `planning` and `cold-read` as well as today's four. Define that default once, as `DEFAULT_LIST_STATUSES` in `model.py`, and use it in `src/chitty/cli.py` and `src/chitty/mcp.py`. `backlog` and `done` stay hidden.
- `chitty next` and `chitty run` never pick `planning` or `cold-read` tickets. `src/chitty/selection.py` already ignores statuses it does not rank, and `MODE_STATUSES` in `src/chitty/store.py` stays as it is.
- `src/chitty/roles/plan.md`: move a ticket to `planning` while writing it, to `cold-read` while a reader works on it, back to `planning` for the outcomes, then to `todo`.
- Docs that name the statuses or the list default: the `status` row in `PLAN.md` "Task file", the `list` bullet in "CLI", the glyph list and list default in `README.md`, and the MCP list tool description. In `PLAN.md` "Pipeline and feedback", delete "Until it lands the statuses above stand."
- Update the existing tests that assert the default list: `tests/test_cli.py` around lines 1296 and 1304. In the `chitty list --help` test, assert `planning` and `cold-read` as separate words, because Click wraps help text.

Out of scope:
- Transitions stay unenforced: any status may follow any other, as today.
- `chitty run` running cold reads (TASK-259); `queued` and `blocked_by` flags (TASK-70, TASK-74).

Put new tests in `tests/test_statuses_planning.py`. Each fails today, because both statuses are rejected.

## Acceptance Criteria

- [x] `chitty add -s planning -d TEXT` and `chitty edit -s cold-read` succeed, and MCP edit accepts both statuses.
- [x] `chitty list` with no `-s` shows a `planning` and a `cold-read` ticket, as `📝 plan` and `🔎 cold`, and still hides `backlog` and `done`; MCP list without a status filter returns the same tickets.
- [x] After `chitty add -s planning -d x`, and `chitty add -d x` followed by `chitty edit -s cold-read`, `chitty next` exits 3 with `no next ticket` on stderr. Today this fails at the first `add`.
- [x] `chitty guide plan` tells planners to use `-s planning` and `-s cold-read`, and `PLAN.md` and `README.md` list both statuses.

## Plan

Add planning and cold-read to model validation, display metadata, and MCP Literal types. Centralize default list statuses and use them in CLI/MCP; update planning guide, status documentation, and existing help/list assertions. Add focused regression coverage for CLI/MCP acceptance, default lists, next selection, guide, and docs; verify regression tests fail before implementation, then run format and full checks.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-255/1`. Check it against the current criteria; do not trust it. It asserts only `cold-read` in the help-text test; add `planning`.

Verified all four acceptance criteria: CLI/MCP status writes, CLI/MCP default lists with backlog/done excluded, next exits 3 for planning/cold-read, and guide/docs mention both statuses. Regression tests failed before implementation; format and full check pass (476 Python suites plus Node tests). chitty fix completed with existing unrelated warnings.

Reviewed: make format && make check passed, including 476 Python and 27 Node tests.
1: pass - CLI and MCP status writes are tested.
2: pass - CLI glyphs and MCP default list filtering are tested.
3: pass - next exits 3 with no next ticket.
4: pass - planning guide and both documents include the statuses.

## Summary

Implemented planning and cold-read statuses, list defaults, guide and docs. Verified all four criteria; make format and make check pass. Commits: b9a1aee and 3c61e3d (Task: TASK-255). Follow-up: none.

## History

- 2026-11-11T10:02:51Z jolly-heron → backlog
- 2026-11-11T10:18:43Z vivid-yellowhammer: changed description
- 2026-11-11T10:36:54Z vivid-yellowhammer: changed description
- 2026-11-11T10:44:16Z vivid-yellowhammer: changed labels, description, acceptance criteria
- 2026-11-11T10:49:39Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T10:52:00Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T10:52:01Z vivid-yellowhammer: changed notes
- 2026-11-11T10:52:02Z vivid-yellowhammer backlog → todo
- 2026-11-11T11:39:07Z vivid-yellowhammer: changed description
- 2026-11-11T12:02:40Z youthful-wren todo → doing
- 2026-11-11T12:03:01Z youthful-wren: wrote the plan
- 2026-11-11T12:09:20Z youthful-wren: changed notes, summary; ticked acceptance criteria
- 2026-11-11T12:09:20Z youthful-wren doing → review
- 2026-11-11T12:11:51Z vivid-dormouse: changed notes; ticked acceptance criteria
- 2026-11-11T12:11:51Z vivid-dormouse review → done
