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
- While the task's status is `review`, any edit with `--set-ac` is refused with `--set-ac is not allowed while a task is in review`, because a reviewer must judge the text that was written. That covers the review transition itself and a separate edit before it. Make it the first check in `check_edit` in `store.py`, before the `--note`, `Reviewed:` and verdict checks, so it is the message the user sees. To reword a criterion, the ticket goes back to `doing` first.
- Multi-line text is refused by the existing single-line check, as for `--ac`.
- History records it as `changed acceptance criteria`, as for `--ac` and `--rm-ac`.

Behaviour lives in the model and store, so CLI and MCP cannot diverge. Add `set_criteria: Sequence[tuple[int, str]] = ()` to `Edit` in `src/chitty/store.py`, pass it to `Task.with_criteria` in `src/chitty/model.py` (which already validates indices for the other options), and add it to the History check near `store.py:1467`. In `src/chitty/cli.py`, `--set-ac` is a `click.option` with `nargs=2`, `type=(int, str)` and `multiple=True`. In `src/chitty/mcp.py`, the `edit` tool takes `set_ac: list[tuple[int, str]] | None`; clients send `"set_ac": [[2, "new text"]]`.

Also add `[--set-ac N TEXT]` to the `chitty edit` synopsis in `PLAN.md`.

No `__version__` bump: this changes no file `chitty init` writes.

Out of scope: reordering criteria, and replacing a criterion's text while keeping its tick.

## Acceptance Criteria

- [ ] A CLI test edits criterion 2 of 3, ticked beforehand, with `--set-ac 2 TEXT` and shows the criteria in their old order with 2 reworded and unticked; the worker records that it failed first
- [ ] Tests show `--set-ac` with an out-of-range number, and with a number also given to `--rm-ac`, failing with the messages in the description and leaving the file unchanged
- [ ] A test in `tests/test_mcp.py` shows the MCP `edit` tool doing the same replacement with `set_ac`
- [ ] Tests show `--set-ac` refused with the message in the description while the task is in `review`, both on its own and in a `review` → `done` edit with a complete `Reviewed:` note and verdicts, leaving the file unchanged

## Notes

Cold read by a fresh Haiku subagent, 2026-11-07, started with `chitty guide cold-read TASK-226`, kept as `refs/cold-read/TASK-226/1`. It built the ticket from the description: the CLI tests failed first (`No such option '--set-ac'`), then passed, and `make check` passed with no version bump. It confirmed click's `nargs=2` form, FastMCP's `list[tuple[int, str]]`, numbering with `--ac` in the same edit, and that refused edits leave the file unchanged. Outcomes:

- Fixed, serious: a reviewer could reword a criterion in the same edit that passes it, so the verdict covered text it never judged. A review transition now refuses `--set-ac`, with a new criterion.
- Fixed: the duplicate-N message is now named.
- Fixed: empty text keeps the existing `acceptance criterion must not be empty`; stated.
- Fixed: the MCP JSON shape is now stated, and `--set-ac` comes first in the conflict check so the messages match.
- Rejected: `--uncheck` already lets a `done` ticket have an unticked criterion, and `--ac` and `--rm-ac` in review transitions are not guarded either; separate from this ticket.
- The review rule is new behaviour, so a second read follows.

Second cold read by a fresh Haiku subagent, 2026-11-07, kept as `refs/cold-read/TASK-226/2`. Every message in the description came out as written, the tests failed first and `make check` passed. Outcomes:

- Fixed, serious: the review rule covered only the transition edit, so a reviewer could reword with a plain `--set-ac` edit while in review and then pass it. `--set-ac` is now refused whenever the status is `review`, and the third criterion covers both cases.
- Fixed: the rule is the first check in `check_edit`, so its message wins over the note and verdict checks; stated.
- Fixed: multi-line text is refused by the existing single-line check; stated.
- Rejected here, filed separately: `--ac` and `--rm-ac` have the same gap during review. That is existing behaviour, wider than this option.
- Rejected: testing the MCP JSON wire shape end to end, because FastMCP validates `list[tuple[int, str]]` on the same path, and the other MCP tools are tested the same way.
- The rule changed again, so a third read follows.

## History

- 2026-11-07T09:37:44Z vivid-dormouse → backlog
- 2026-11-07T10:04:53Z vivid-dormouse: changed description, acceptance criteria, notes
- 2026-11-07T10:09:04Z vivid-dormouse: changed description, acceptance criteria, notes
