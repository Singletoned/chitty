---
title: Skip ticket IDs cited with another project's name in the `edit -s todo` listing
status: doing
labels:
  - bug
depends_on:
  - TASK-YST8KG
created: 2026-11-26
provisional: true
---

## Description

### Why

On 2026-11-26, after `chitty edit -s todo`, Chitty listed `TASK-217 done ...` and `TASK-164 done ...` for a ticket whose Description cited "echonomicon `TASK-217`" and "echonomicon `TASK-164`": unrelated tickets in this repository. A planner skimming that list can take one for a real dependency or a done duplicate. Decided (the person, 2026-11-26): skip an ID preceded by a project name, and tell planners to cite other repositories that way.

### Change

- `ids.ticket_references(text, prefixes, *, foreign)` in `src/chitty/ids.py` gets a required keyword argument `foreign: Collection[str]`, project names. A match is skipped when the text just before it is one of those names (compared case-insensitively), then exactly one space character, then optionally one backtick directly before the ID, and the character before the name is not in `[A-Za-z0-9._-]` (or the name starts the text). Newlines and tabs do not count as the space.
- `Repo.referenced_tasks` (`src/chitty/store.py`, the listing `chitty edit -s todo` prints) passes `config.registered_projects()` minus `self.config.project`. The registry is per machine, which is fine for a listing that only informs the planner.
- The renumbering call in `_plan_provisional_renumbering` passes `foreign=()`, so renumbering stays the same on every machine. This ticket depends on TASK-YST8KG, which changes the same call. Update the four test calls in `tests/test_promote_references.py` to pass `foreign=()`.
- Leftover test registrations on a machine (TASK-310) can hide a real citation from this listing; that is accepted, since the listing only informs the planner.
- In `src/chitty/roles/plan.md`, in the bullet that begins "Put paths, globs, commands, IDs, and code in backticks", add: "Cite another project's ticket with its name first, for example `other TASK-4`." About 12 more words; nothing cut, because a misread citation costs a wrong dependency or archive.

### Out of scope

Placeholder IDs in examples; other forms such as `other#TASK-4`; renumbering (TASK-YST8KG).

## Acceptance Criteria

- [ ] In `tests/test_promote_references.py`, a Hypothesis property test (`@settings(max_examples=examples(N))`) builds text from the same parts and `SEPARATORS` as the existing tests, putting a foreign name (drawn to match `PROJECT_NAME_RE` in `src/chitty/config.py`, in any case), then one space and optionally a backtick, before some of the references. `ticket_references(text, PREFIXES, foreign=names)` returns exactly the other references, in order and without repeats; with `foreign=()` it returns what it returns today. A fixed case: with `foreign=("other",)`, `x_other TASK-9` still returns `TASK-9`. Fails without the change (by `TypeError` today, since the keyword does not exist).
- [ ] A new test in `tests/test_promote_references_cli.py`, which alone registers `other` with `register_project("other", <a temporary directory>)`, replaces `TASK-1`'s Description from `setUp` with ``See other `TASK-9` and TASK-2.`` and its criterion with `Done.`, then runs `chitty edit TASK-1 -s todo`: the output lists `TASK-2 doing Second task` and has no line for `TASK-9`. Fails without the change. Regression tests: the existing tests in both files pass unchanged apart from `foreign=()`. `make check` passes.

## Plan

Add property and CLI regression tests, verify they fail, then filter foreign-qualified references only in the planner listing; preserve deterministic renumbering and update planner guidance.

## Notes

Decided: the renumbering call already exists on this branch -> pass foreign=() there, because the required deterministic behavior does not depend on its exact surrounding implementation.

## History

- 2026-11-26T10:54:44Z calm-ochre-quail → backlog
- 2026-11-26T10:54:47Z calm-ochre-quail: changed notes
- 2026-11-26T10:56:51Z calm-ochre-quail: changed labels, notes
- 2026-11-26T11:11:27Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:27Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:18:12Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:18:12Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:18:23Z calm-ochre-quail: changed acceptance criteria
- 2026-11-26T11:19:56Z calm-ochre-quail: changed dependencies, description, acceptance criteria
- 2026-11-26T11:19:56Z calm-ochre-quail cold-read → todo
- 2026-11-26T12:12:20Z vivid-indigo-gannet todo → doing
- 2026-11-26T12:16:09Z vivid-indigo-gannet: wrote the plan
- 2026-11-26T12:16:43Z vivid-indigo-gannet: changed notes
