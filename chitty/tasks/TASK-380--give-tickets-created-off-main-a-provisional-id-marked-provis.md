---
title: "Give tickets created off `main` a provisional ID marked `provisional: true`"
status: cold-read
labels:
  - needs-minor
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), only `main` hands out sequential ticket numbers. A ticket created anywhere else (a follow-up found on a ticket branch, possibly in a container that cannot see other branches) gets a provisional ID that cannot clash and is visibly marked for renumbering. `TASK-381` renumbers provisional tickets on `main` later; that is cosmetic, so provisional IDs must work everywhere until then.

Today plain `chitty add` in a linked worktree files the ticket in the `backlog` context with a numeric random ID (`resolve_add_target` in `src/chitty/store.py`), and any other new ID on a branch is sequential (`Repo.next_number`).

Decisions:

- "Off `main`" means the checkout's current branch is not the main branch (`Repo._main_branch()`), including a detached `HEAD`, a linked worktree, or a main checkout or plain clone switched to another branch.
- Pure function `provisional_suffix(draw: Callable[[int], int]) -> str` in `src/chitty/ids.py`: 6 characters from module constant `PROVISIONAL_ALPHABET = "ABCDEFGHJKMNPQRSTVWXYZ23456789"`, `draw(n)` returning an index below `n`, and at least one letter (redraw until it has one). Production passes `secrets.randbelow`. The result always parses: `TaskId.parse(f"{prefix}-{suffix}").number == suffix`, a `str`, never an `int`. `ids.ID_RE` already accepts such suffixes; do not change it.
- New optional frontmatter field `provisional: bool` in `Frontmatter` (`src/chitty/model.py`), written as `provisional: true` and omitted when false. Add its row to the table in `docs/plan/task-file.md`.
- `Repo.add`, `Repo.move` and `Repo.renumber` (`src/chitty/store.py`) get new IDs from one new method `Repo.new_id(context) -> tuple[TaskId, bool]`: off `main`, a provisional ID (retrying up to `RANDOM_ID_ATTEMPTS` against IDs already in use) and `True`; on `main`, `next_number` as today and `False`. The ticket's `provisional` field is set to that boolean, so `move` on `main` of a provisional ticket also clears it.
- Contexts with `random_ids = true` keep their numeric random IDs everywhere and are never provisional: their IDs cannot clash already.
- Remove the rule filing plain `add` in a linked worktree into `backlog`: with no `-c`, `add` uses `default_context` everywhere. Update `tests/test_backlog_context.py` to match and replace the `Plain chitty add in a linked worktree files there` sentence in `docs/plan/ids.md` with the provisional rule. Label `needs-minor`.

Out of scope: renumbering (`TASK-381`), where tickets are read from (`TASK-378`), and changing `next_number` (`TASK-379`).

Tests: a Hypothesis property for `provisional_suffix` in a new `tests/test_property_provisional_id.py`, generating `draw` as a seeded sequence of indices (`st.randoms` or a list of integers) and prefixes matching `[A-Z]+`. Real-Git tests through the CLI in a new `tests/test_provisional_ids.py`, inheriting `RepoTestCase`. The store behaviour has no property: a fixed set of checkout states (main, linked worktree on a branch, main checkout switched to a branch) by commands (`add`, `move`), each tested.

## Acceptance Criteria

- [ ] The `provisional_suffix` property passes for generated draws and prefixes (length 6, only `PROVISIONAL_ALPHABET`, at least one letter, `TaskId.parse` gives back the suffix as a `str`) and fails against a `NotImplementedError` stub
- [ ] `chitty add` with no `-c` in a linked worktree on branch `feature`, and in the main checkout switched to `feature`, each creates a ticket in `default_context` (not `backlog`) whose ID suffix contains a letter and whose file has `provisional: true`; the linked-worktree case fails before the change
- [ ] On `main`, `chitty add` gives the next sequential number and the file has no `provisional` key; `chitty move` to another context on `feature` gives a provisional ID with `provisional: true`, and `chitty move` of that provisional ticket on `main` gives a sequential ID and removes the key
- [ ] `chitty add -c backlog` on `feature` still gives a numeric random ID with no `provisional` key; `show`, `edit` and `list` work on a provisional ticket by its ID
- [ ] `docs/plan/task-file.md` lists `provisional`, `docs/plan/ids.md` states the provisional rule in place of the linked-worktree `backlog` sentence, and `make check` passes

## History

- 2026-11-18T16:20:07Z lively-quartz-crane → backlog
- 2026-11-18T16:22:50Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T16:22:50Z lively-quartz-crane backlog → planning
- 2026-11-18T16:23:29Z lively-quartz-crane planning → cold-read
