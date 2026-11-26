---
title: Renumber any ticket to the next number and rewrite references to it
status: cold-read
labels:
  - bug
depends_on:
  - TASK-YST8KG
created: 2026-11-24
---

## Description

### Why

In echonomicon on 2026-11-24, after a plan branch landed, `chitty renumber chitty/tasks/TASK-BCHE6A--*.md` failed with "TASK-BCHE6A is used by no other file; use `chitty move` to give it a new ID", and `chitty move TASK-BCHE6A tasks` failed with "already in context tasks". There is no way to renumber one ticket whose ID is not shared, so the planner kept the provisional IDs. The person, 2026-11-26: "we need a general renumbering system, eg for renumbering temp tickets".

### Change

`Repo.renumber(path)` (`src/chitty/store.py`) keeps today's behaviour when other files share the ticket's ID. When no other file does, it renumbers that one ticket the way `renumber_provisional` renumbers provisional ones: on `main` (or outside Git) only, the same `ProvisionalOffMain` refusal otherwise; the next number from `plan_renumbering`; references to the old ID rewritten in every writable ticket; `moved_from` recorded and `provisional` cleared; one commit. Do it by letting `_plan_provisional_renumbering` take the candidate IDs (today: every provisional ticket in a sequential context; here: the one ticket), and by letting `plan_renumbering` accept numbered candidates as well as provisional ones (drop its "is not provisional" refusal; still refuse duplicates). A random-ID context refuses with a clear error, since its numbers are not sequential.

Update the `renumber` help in `src/chitty/cli.py` to say a ticket with a unique ID is renumbered with its references rewritten.

### Out of scope

Accepting an ID instead of a path; choosing the new number; renumbering on landing (TASK-340); restarting numbering (TASK-W74AVC).

## Acceptance Criteria

- [ ] In `tests/test_renumber.py` (no Git, so numbers are sequential as on `main`), with `TASK-3` named by `TASK-4`'s `depends_on` and Description: `chitty renumber chitty/tasks/TASK-3--dependent.md` gives it the next number, records `moved_from: TASK-3`, and rewrites `TASK-3` to the new ID in the other ticket's `depends_on` and Description; `chitty check` passes. The same works for a provisional ticket (`provisional: true`, written into the file directly) and clears `provisional`. Replace the `TASK-3 is used by no other file` case in `test_refuses_without_changing_anything`. Fails without the change.
- [ ] In a Git repository on a branch other than `main`, `chitty renumber <path>` of a ticket whose ID is used by no other file exits 1 with the `ProvisionalOffMain` message and changes nothing. Regression tests: `test_renumbers_only_that_file_and_lists_references` and the other renumber and provisional-renumbering tests pass. `make check` passes.

## History

- 2026-11-24T22:21:23Z zesty-coral-newt → backlog
- 2026-11-24T22:21:24Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:36Z zesty-coral-newt: changed labels
- 2026-11-26T11:11:51Z calm-ochre-quail: changed title, notes
- 2026-11-26T11:11:51Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:20:40Z calm-ochre-quail: replaced notes; changed dependencies, description, acceptance criteria
- 2026-11-26T11:20:40Z calm-ochre-quail to-plan → cold-read
