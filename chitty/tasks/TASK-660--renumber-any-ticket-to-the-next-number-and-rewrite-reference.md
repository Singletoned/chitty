---
title: Renumber any ticket to the next number and rewrite references to it
status: doing
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

`Repo.renumber(path)` (`src/chitty/store.py`) keeps today's behaviour when other files share the ticket's ID. When no other file does, it renumbers that one ticket by reusing the body of `renumber_provisional` with the ticket as the only candidate: references to the old ID rewritten in every writable ticket, `moved_from` recorded, `provisional` cleared, one commit with the message `chitty: renumber <new ID> <title>`. It returns that change with `()` as the references, since none are left to check.

- `_plan_provisional_renumbering` takes a required `candidates` argument: `None` for today's selection (every provisional ticket in a sequential context), or a tuple of IDs. Update its existing callers in the tests to pass `None`. It refuses with ``ProvisionalOffMain`` off `main` before anything else, as today, and refuses with a clear error when a given candidate is in a random-ID context.
- `plan_renumbering` (`src/chitty/renumbering.py`) accepts numbered candidates as well as provisional ones: drop its "is not provisional" refusal and the matching assertion in `tests/test_property_renumbering.py`, keeping the duplicate refusal.
- Update the `renumber` help in `src/chitty/cli.py` to say a ticket with a unique ID is renumbered and its references rewritten.

### Out of scope

Accepting an ID instead of a path; choosing the new number; renumbering on landing (TASK-340); restarting numbering (TASK-W74AVC).

## Acceptance Criteria

- [x] In a new `CliTestCase` subclass in `tests/test_renumber.py` (no Git, so numbers are sequential as on `main`), a test adds a ticket `Target` and a ticket `Uses` with `--depends-on` naming `Target` and a Description mentioning `Target`'s ID. `chitty renumber <Target path>` gives `Target` the next number, records `moved_from` with the old ID, and rewrites the old ID to the new one in `Uses`'s `depends_on` and Description; `chitty check` then exits 0. The same works for a ticket made provisional (`provisional: true` written into its file directly), and clears `provisional`. In `TestRenumber`, drop the `TASK-3 is used by no other file` case from `test_refuses_without_changing_anything` and update `test_help` for the new help text. Fails without the change.
- [x] In `tests/test_provisional_preflight_errors.py`, using the Git fixture helpers of `TestProvisionalPreflight` (`init_git`, `file`, `commit`), a test on a feature branch runs `chitty renumber <path>` for a numbered ticket with a unique ID: it exits 1 with the `ProvisionalOffMain` message and the files are unchanged. Regression tests: `test_renumbers_only_that_file_and_lists_references`, and the provisional-renumbering tests after passing the candidates argument, pass. `make check` passes.

## Plan

Extend the existing provisional renumber planner and execution to accept explicit candidates, route unique IDs through it, and retain duplicate-ID behavior. Add CLI and preflight regression tests, verify they fail before the fix, then run formatting and checks.

## Notes

Before the fix, the unique numbered and provisional CLI cases fail with the no-other-file error; the feature-branch case fails because it reports that error instead of ProvisionalOffMain.

## Summary

Unique sequential-context tickets now renumber through the existing reference-rewriting planner; shared IDs retain their existing behavior. Verified failing tests before the fix, targeted regression tests, and make check (1243 passed).

## History

- 2026-11-24T22:21:23Z zesty-coral-newt → backlog
- 2026-11-24T22:21:24Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:36Z zesty-coral-newt: changed labels
- 2026-11-26T11:11:51Z calm-ochre-quail: changed title, notes
- 2026-11-26T11:11:51Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:20:40Z calm-ochre-quail: replaced notes; changed dependencies, description, acceptance criteria
- 2026-11-26T11:20:40Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:20:52Z calm-ochre-quail: changed acceptance criteria
- 2026-11-26T11:22:30Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T11:22:30Z calm-ochre-quail cold-read → todo
- 2026-11-26T11:55:31Z zesty-zinc-puffin todo → doing
- 2026-11-26T11:59:52Z zesty-zinc-puffin: wrote the plan
- 2026-11-26T12:00:46Z zesty-zinc-puffin: changed notes
- 2026-11-26T12:08:41Z zesty-zinc-puffin: changed summary; ticked acceptance criteria
