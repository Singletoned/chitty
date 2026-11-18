---
title: Renumber provisional tickets on `main` with `chitty renumber`
status: cold-read
depends_on:
  - TASK-389
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` and `provisional: true` (`TASK-380`, `TASK-389`). Once it reaches `main`, it should get an ordinary sequential number. This is cosmetic: provisional IDs work everywhere, so renumbering is one idempotent command a person or script can run at any time.

Starts after `TASK-389` lands.

Decisions:

- `chitty renumber` with no `PATH` renumbers every provisional ticket. `PATH` becomes optional; `chitty renumber PATH` behaves exactly as today.
- On `main` (not off `main` as `TASK-389` defines it): every ticket file in this checkout with `provisional: true`, active or archived, in every context, gets the next sequential number of its context. Order: sorted by `TaskId` within each context, so the result is deterministic. Each file is renamed (same slug), loses `provisional`, gets `moved_from` set to its provisional ID (replacing any earlier value), and gets a History event `renumbered from <old ID>`.
- Every literal mention of each old ID in every ticket file in the checkout is replaced by the new ID: frontmatter (`depends_on`, `parent`, `moved_from` of other tickets) and body text. A mention is the exact upper-case ID not preceded by a letter, digit or `-` and not followed by a letter or digit, so `TASK-K7Q2MX--slug.md` is rewritten and `XTASK-K7Q2MX`, `TASK-K7Q2MXY` and lower-case branch names such as `task-k7q2mx` are not. Commit messages and other files are left alone.
- All of it is one batched write with at most one autocommit, as `archive_done` does (`Repo.finalize`).
- Idempotent: with no provisional ticket it writes nothing, makes no commit, prints `nothing to renumber` and exits 0. Off `main` it changes nothing, prints that provisional tickets are renumbered on `main`, and exits 0.
- Pure core in a new module `src/chitty/renumbering.py`, created first with these names raising `NotImplementedError`: `plan_renumbering(used: Mapping[str, set[int]], provisional: Sequence[TaskId]) -> dict[TaskId, TaskId]` (`used` maps each prefix to the sequential numbers taken in its context, including those `next_number` counts) and `replace_ids(text: str, mapping: Mapping[TaskId, TaskId]) -> str`. `Repo` gathers the inputs and writes the files; `cli.py` stays thin. No MCP tool.
- Update the `renumber` help in `src/chitty/cli.py` and `docs/plan/cli.md`.

Tests: Hypothesis properties in a new `tests/test_property_renumbering.py`; generate prefixes matching `[A-Z]+`, sets of used numbers, provisional IDs from `ids.provisional_suffix` with random draws, and text mixing mentions, bounded and unbounded look-alikes, lower-case forms and unrelated text. Real-file CLI tests in a new `tests/test_renumber_provisional.py`, inheriting `RepoTestCase` from `tests/support.py` and running `git init`; create provisional tickets with `chitty add` on a branch, then `git merge` into `main`.

## Acceptance Criteria

- [ ] `plan_renumbering` property: for generated inputs, each prefix's provisional IDs map, in sorted `TaskId` order, onto exactly the consecutive numbers above the highest used number of that prefix (or from 1), no new ID is in `used`, and every input ID appears once; it fails against the stub
- [ ] `replace_ids` property: every bounded mention of an old ID becomes its new ID, text with no bounded mention is unchanged (including look-alikes and lower-case forms), and applying it twice equals applying it once; it fails against the stub
- [ ] On `main`, with an active and an archived provisional ticket and another ticket that lists one in `depends_on` and mentions both in its Description, `chitty renumber` gives both sequential IDs, renames the files, removes `provisional`, sets `moved_from`, rewrites the other ticket's `depends_on` and Description, and makes one commit; running it again prints `nothing to renumber` and makes no commit
- [ ] Off `main`, `chitty renumber` changes no file, makes no commit and exits 0; `chitty renumber PATH` for two files sharing an ID behaves as before; `make check` passes

## History

- 2026-11-18T16:20:09Z lively-quartz-crane → backlog
- 2026-11-18T16:23:20Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:28:42Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:30:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:30:08Z lively-quartz-crane backlog → planning
- 2026-11-18T16:30:16Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:30:29Z lively-quartz-crane planning → cold-read
