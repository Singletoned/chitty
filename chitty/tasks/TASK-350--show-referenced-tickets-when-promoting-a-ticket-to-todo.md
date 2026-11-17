---
title: Show referenced tickets when promoting a ticket to todo
status: cold-read
depends_on:
  - TASK-356
created: 2026-11-16
---

## Description

`src/chitty/roles/plan.md` tells planners to re-check claims about other tickets just before promoting, because they can land during the read. Make `chitty edit -s todo` show those tickets instead, so the planner sees what changed without being told to look.

Decisions:

- Add a pure function `ticket_references(text: str, prefixes: Collection[str]) -> list[TaskId]` in `src/chitty/ids.py`. It returns each ID in `text` whose prefix is exactly one of `prefixes` (upper-case, case-sensitive), in order of first appearance, without repeats. An ID counts only when the character before it is not a letter, digit or `-`, and the character after it is not a letter or digit. So `TASK-12.` and `` `TASK-12` `` give `TASK-12`; `XTASK-12`, `task-12` and `UTF-8` give nothing when the prefixes are `TASK` and `HUMAN`.
- Add `Repo.referenced_tasks(stored: StoredTask) -> list[tuple[TaskId, StoredTask | None]]` in `src/chitty/store.py`. It scans the Description and every criterion's text, with the prefixes of every context in the repo, leaves out the ticket's own ID, and looks each ID up with `Repo.lookup` from `TASK-356` (`None` when no ticket has it).
- `chitty edit` in `src/chitty/cli.py`, when the edit changes the status to `todo` from another status, prints after its `updated` line one line per reference, in order: `<ID> <status> <title>`, or `<ID> no such task`. It prints nothing extra when the status was already `todo`, for other statuses, or with `--json`.
- Replace the plan guide bullet `Re-check claims about other tickets just before promoting, because they can land during the read.` with `` `chitty edit -s todo` lists the tickets a ticket mentions: check that its claims about them still hold. ``

Tests use Hypothesis, as `tests/test_property_next.py` does. Put them in a new `tests/test_promote_references.py`; CLI tests inherit `CliTestCase` from `tests/test_cli.py`.

Out of scope: the MCP edit tool, references in Plan or Notes, and lower-case IDs.

## Acceptance Criteria

- [ ] Property test with Hypothesis on `ticket_references`: for any list of IDs (prefix drawn from a fixed set, number 1 to 9999) joined by separators drawn from space, newline, comma, full stop, backtick, `(` and `)`, the result is that list with repeats removed, first appearance kept. A second property: for any text (`st.text()`) and prefix set, the call never raises, and every returned ID has a prefix in the set and appears in the text. Fails on `main`, where the function does not exist.
- [ ] Example tests on `ticket_references` with prefixes `TASK` and `HUMAN`: `XTASK-12`, `task-12`, `UTF-8` and `TASK-12a` each give `[]`, and `see TASK-12.` gives `[TASK-12]`.
- [ ] CLI test: `TASK-1` in `planning` mentions `TASK-2` (a `doing` ticket) in its Description, `TASK-1` itself and `TASK-9` (no such ticket) in a criterion, and `TASK-2` again. `chitty edit TASK-1 -s todo` prints, after the `updated` line, exactly `TASK-2 doing <title of TASK-2>` then `TASK-9 no such task`. A second `chitty edit TASK-1 -s todo`, a `chitty edit TASK-1 -s doing`, and `-s todo --json` from `planning` print no reference lines.
- [ ] The plan guide bullet is replaced as the Description says, and `tests/test_guide_plan_restored.py` checks the new sentence instead of `because they can land during the read`. `make check` passes.

## History

- 2026-11-16T10:00:02Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:46Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:02:05Z kind-umber-toad: changed dependencies, description, acceptance criteria
- 2026-11-17T16:02:05Z kind-umber-toad planning → cold-read
- 2026-11-17T16:02:13Z kind-umber-toad: changed description
