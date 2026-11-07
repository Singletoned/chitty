---
title: Replace an acceptance criterion in place with `chitty edit --set-ac`
status: backlog
priority: medium
created: 2026-11-07
---

## Description

Rewording one acceptance criterion today takes `--rm-ac N` plus `--ac TEXT`, which moves it to the end of the list. Keeping the order means removing and re-adding every criterion after it too. On 2026-11-07 rewording `TASK-63`'s first criterion took two more edits to put the order back, and criterion numbers quoted in notes went stale in between.

Add `--set-ac N TEXT` to `chitty edit`, repeatable, which replaces criterion N's text in place:

- N is 1-based and counts the list before this edit, like `--rm-ac`, `--check` and `--uncheck`.
- The criterion becomes unticked, because its new text has not been verified.
- Out-of-range N fails with the same kind of message as `--rm-ac` (`--set-ac 5: there are 2 acceptance criteria`). The same N given to `--set-ac` and to `--rm-ac`, `--check` or `--uncheck` fails as those already do between each other (`criterion 2 is given to both --set-ac and --rm-ac`), and the same N twice in `--set-ac` fails with `criterion 1 is given more than once to --set-ac`. Empty text fails with the existing `acceptance criterion must not be empty`. List `--set-ac` first in `with_criteria`'s conflict check, so its messages read as above.
- A review transition (`review` → `done` or `review` → `doing`) refuses `--set-ac` with `--set-ac is not allowed in a review transition`, because a reviewer must judge the text that was written. Add this to `check_edit` in `store.py`.
- History records it as `changed acceptance criteria`, as for `--ac` and `--rm-ac`.

Behaviour lives in the model and store, so CLI and MCP cannot diverge. Add `set_criteria: Sequence[tuple[int, str]] = ()` to `Edit` in `src/chitty/store.py`, pass it to `Task.with_criteria` in `src/chitty/model.py` (which already validates indices for the other options), and add it to the History check near `store.py:1467`. In `src/chitty/cli.py`, `--set-ac` is a `click.option` with `nargs=2`, `type=(int, str)` and `multiple=True`. In `src/chitty/mcp.py`, the `edit` tool takes `set_ac: list[tuple[int, str]] | None`; clients send `"set_ac": [[2, "new text"]]`.

Also add `[--set-ac N TEXT]` to the `chitty edit` synopsis in `PLAN.md`.

No `__version__` bump: this changes no file `chitty init` writes.

Out of scope: reordering criteria, and replacing a criterion's text while keeping its tick.

## Acceptance Criteria

- [ ] A CLI test edits criterion 2 of 3, ticked beforehand, with `--set-ac 2 TEXT` and shows the criteria in their old order with 2 reworded and unticked; the worker records that it failed first
- [ ] Tests show `--set-ac` with an out-of-range number, and with a number also given to `--rm-ac`, failing with the messages in the description and leaving the file unchanged
- [ ] A test in `tests/test_mcp.py` shows the MCP `edit` tool doing the same replacement with `set_ac`
- [ ] A test shows a `review` → `done` edit with `--set-ac` refused with the message in the description and the file unchanged

## Notes

Cold read by a fresh Haiku subagent, 2026-11-07, started with `chitty guide cold-read TASK-226`, kept as `refs/cold-read/TASK-226/1`. It built the ticket from the description: the CLI tests failed first (`No such option '--set-ac'`), then passed, and `make check` passed with no version bump. It confirmed click's `nargs=2` form, FastMCP's `list[tuple[int, str]]`, numbering with `--ac` in the same edit, and that refused edits leave the file unchanged. Outcomes:

- Fixed, serious: a reviewer could reword a criterion in the same edit that passes it, so the verdict covered text it never judged. A review transition now refuses `--set-ac`, with a new criterion.
- Fixed: the duplicate-N message is now named.
- Fixed: empty text keeps the existing `acceptance criterion must not be empty`; stated.
- Fixed: the MCP JSON shape is now stated, and `--set-ac` comes first in the conflict check so the messages match.
- Rejected: `--uncheck` already lets a `done` ticket have an unticked criterion, and `--ac` and `--rm-ac` in review transitions are not guarded either; separate from this ticket.
- The review rule is new behaviour, so a second read follows.

## History

- 2026-11-07T09:37:44Z vivid-dormouse → backlog
- 2026-11-07T10:04:53Z vivid-dormouse: changed description, acceptance criteria, notes
