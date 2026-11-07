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
- Out-of-range N fails with the same kind of message as `--rm-ac` (`--set-ac 5: there are 2 acceptance criteria`). The same N given to `--set-ac` and to `--rm-ac`, `--check` or `--uncheck` fails as those already do between each other (`criterion 2 is given to both --set-ac and --rm-ac`), as does the same N twice in `--set-ac`.
- History records it as `changed acceptance criteria`, as for `--ac` and `--rm-ac`.

Behaviour lives in the model and store, so CLI and MCP cannot diverge. Add `set_criteria: Sequence[tuple[int, str]] = ()` to `Edit` in `src/chitty/store.py`, pass it to `Task.with_criteria` in `src/chitty/model.py` (which already validates indices for the other options), and add it to the History check near `store.py:1467`. In `src/chitty/cli.py`, `--set-ac` is a `click.option` with `nargs=2`, `type=(int, str)` and `multiple=True`. In `src/chitty/mcp.py`, the `edit` tool takes `set_ac: list[tuple[int, str]] | None`.

Also add `[--set-ac N TEXT]` to the `chitty edit` synopsis in `PLAN.md`.

No `__version__` bump: this changes no file `chitty init` writes.

Out of scope: reordering criteria, and replacing a criterion's text while keeping its tick.

## Acceptance Criteria

- [ ] A CLI test edits criterion 2 of 3, ticked beforehand, with `--set-ac 2 TEXT` and shows the criteria in their old order with 2 reworded and unticked; the worker records that it failed first
- [ ] Tests show `--set-ac` with an out-of-range number, and with a number also given to `--rm-ac`, failing with the messages in the description and leaving the file unchanged
- [ ] A test in `tests/test_mcp.py` shows the MCP `edit` tool doing the same replacement with `set_ac`

## History

- 2026-11-07T09:37:44Z vivid-dormouse → backlog
