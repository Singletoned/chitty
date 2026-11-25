---
title: Mark conflicted tickets in `chitty list` instead of failing
status: cold-read
labels:
  - bug
priority: high
parent: TASK-376
created: 2026-11-20
---

## Description

When Chitty cannot choose a ticket's source, `chitty list`, `chitty next` and the runner fail for every ticket, printing only that one error. Seen 2026-11-25: `TASK-FER4EB` changed on both `task-fer4eb` and `main` (a hand edit on `main`, commit `19109451`), and `chitty list` printed `Error: ticket `TASK-FER4EB` changed on both `task-fer4eb` and `main`` and no tickets. TASK-602 will let `main` be written while a ticket branch also changes the ticket, so this state will be easier to reach.

The two errors come from `ticket_source` in `src/chitty/ticket_source.py`: `ticket <id> has diverged refs: ...` and `ticket <id> changed on both <ref> and <main>`. Listing reaches them through `Repo._tasks_in_location` -> `_source_files` -> `_choose_source` (`src/chitty/store.py`).

Change:

- Raise both as a new `SourceConflict(ChittyError)` in `ticket_source.py`, with the same messages.
- In `_tasks_in_location`, on `SourceConflict` keep the ticket, using its copy on the configured main branch, or the working tree's copy if `main` has none (if neither exists, raise as today), and set a new `StoredTask.conflict: str | None` to the error text.
- Add `conflict: str | None = None` to `TicketFacts` (`src/chitty/selection.py`), set by `_selection_facts` (`src/chitty/store.py`) from `StoredTask.conflict`. The pure `selection.skip_reason` returns `🔀 <error text>` for it before any other reason, so `chitty list` shows it and `chitty next` and `chitty run` (through `selection.choose`) skip it. Add `CONFLICT_GLYPH = "🔀"` beside the other glyphs.
- A ticket that depends on a conflicted one keeps today's broken-dependency marker (`💔`, from the `ChittyError` that `_selection_facts` already catches).
- `chitty list --json` and the MCP `list` tool add `"conflict": "<error text>"` for such tickets only.
- Commands on one ticket (`show`, `edit`, `note` and others that use `Repo.find`) still raise.

No pure function suits: the behaviour is how real Git states reach the listing, so the property runs on real repositories.

Out of scope: preventing the state (TASK-602 warns instead), byte-identical copies wrongly reported as changed on both (TASK-667), and marking tickets whose status comes from another branch (TASK-603).

## Acceptance Criteria

- [ ] A Hypothesis property test with real Git, `@settings(max_examples=examples(25))` as in `tests/test_property_hidden_entries.py`: make 1 to 4 tickets, and give each one of: no conflict, changes on both `task-<n>` and `main` since they split, or diverged `task-<n>` and `origin/task-<n>`. `chitty list` exits 0 and lists every ticket exactly once; exactly the conflicted ones show `🔀` with today's error text, and `chitty list --json` gives exactly those a `conflict` key. Fails today: `chitty list` exits 1 with only the error.
- [ ] In that setup with one conflicted `todo` ticket of `high` priority and one plain `todo` ticket, `chitty next` names the plain ticket; `chitty show` of the conflicted one still fails with today's message. Fails today.
- [ ] Regression tests: the existing tests stay green, including `tests/test_property_ticket_source.py`, `tests/test_list_glyphs.py`, `tests/test_authoritative_listing.py` and `tests/test_source_copy_errors.py` (single-ticket commands keep their messages); `make check` passes.

## History

- 2026-11-20T11:10:11Z lively-bronze-crane → backlog
- 2026-11-25T22:32:49Z calm-ochre-quail: changed notes
- 2026-11-25T23:27:43Z calm-ochre-quail: replaced notes; changed labels, priority, dependencies, description, acceptance criteria
- 2026-11-25T23:27:43Z calm-ochre-quail backlog → planning
- 2026-11-25T23:28:23Z calm-ochre-quail planning → cold-read
- 2026-11-25T23:30:07Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-25T23:30:07Z calm-ochre-quail cold-read → planning
- 2026-11-25T23:30:15Z calm-ochre-quail planning → cold-read
