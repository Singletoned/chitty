---
title: Add a `dropped` status for tickets that will not be done
status: cold-read
labels:
  - needs-minor
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close a ticket is `done`, which (with review on) needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. On 2026-11-22 closing `TASK-451` (superseded) that way was refused as faking a review. Add a terminal status for tickets that will not be done.

Decisions:

- New status `dropped`, last in `STATUSES` in `src/chitty/model.py`, and in the frontmatter `status` `Literal` (`src/chitty/model.py`, around line 176) and the MCP `Status` `Literal` (`src/chitty/mcp.py`, around line 38). Glyph `🚫` (U+1F6AB, natively wide, see `TASK-576`) in `STATUS_GLYPHS`; label `drop` in `STATUS_LABELS`. Not in `DEFAULT_LIST_STATUSES`, so `chitty list` hides it as it hides `done`; `chitty list -s dropped` and `--all` show it.
- `chitty edit <id> -s dropped` (and `chitty add -s dropped`, and MCP) is allowed from every status except `done` (`dropped` from `done` raises `ChittyError` `<id> is done; it cannot be dropped`), and never needs `review`. It needs a reason: the edit must set a non-empty Summary (`--summary`/`--summary-file`, or the MCP summary field), or the ticket must already have a non-empty Summary section; otherwise it raises `ChittyError` `dropping <id> needs a --summary saying why`, and nothing is written. Leaving `dropped` for another status is allowed as for any status (a ticket can be revived).
- `chitty archive` with no ID archives every active ticket whose status is `done` or `dropped` (`Repo` method around `src/chitty/store.py` line 1270); `chitty archive <id>` works on a `dropped` ticket.
- Nothing else changes in this ticket: the runner only selects `todo`, `doing` and `review` (`src/chitty/selection.py` line 29), so it never picks a dropped ticket. A ticket that depends on a dropped ticket stays blocked, since only `done` or archived satisfies a dependency (`src/chitty/store.py` around line 2292); how dependents and release labels treat `dropped` is a later ticket.
- The ticket's branch and worktree, if any, are not touched; the clean-up rule in `AGENTS.md` covers them. Editing a ticket whose latest copy is on a branch is still refused from the main checkout, as for any edit (`TASK-385` covers that).

Tests in a new `tests/test_status_dropped.py`, using `RepoTestCase` and `chitty.cli.cli` through `click.testing.CliRunner` as `tests/test_edit_human.py` does, in a repository with review on:

- From each of `backlog`, `planning`, `todo`, `doing` and `review`: `chitty edit TASK-1 -s dropped --summary "Superseded by TASK-2."` exits 0; the file has `status: dropped`, its Summary section is `Superseded by TASK-2.`, and its History has the transition.
- Without `--summary` on a ticket with no Summary: exits non-zero with the message above and the file is byte-identical to before. On a ticket that already has a Summary: exits 0. `--summary ""`: refused like no summary.
- From `done`: refused with the message above.
- `chitty list` does not show a dropped ticket; `chitty list -s dropped` does, with `🚫` and `drop`.
- `chitty archive` with no ID archives one `done` and one `dropped` ticket and leaves a `todo` one.
- `chitty edit TASK-1 -s todo` from `dropped` exits 0.
- The model round-trips: `parse(render(task))` keeps `status: dropped` (use the existing helpers in `tests/support.py`).

Docs: `docs/plan/task-file.md` (statuses) and the `chitty --help` text for `-s`, if it lists statuses, name `dropped` and say what it is for. The role guides are a later ticket.

## Acceptance Criteria

- [ ] The tests in `tests/test_status_dropped.py` pass, and the edit, list and archive cases fail before the change; record both runs in a note
- [ ] `docs/plan/task-file.md` names `dropped` and what it is for; `make check` passes

## History

- 2026-11-22T22:09:08Z plucky-umber-wren → cold-read
