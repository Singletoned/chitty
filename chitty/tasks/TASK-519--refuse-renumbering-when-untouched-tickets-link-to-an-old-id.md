---
title: Refuse renumbering when untouched tickets link to an old ID
status: cold-read
depends_on:
  - TASK-391
parent: TASK-391
created: 2026-11-21
---

## Description

Extend the read-only planner `Repo._plan_provisional_renumbering` in `src/chitty/store.py` (landed by `TASK-391`) so it refuses a plan that would leave a structured link pointing at a renumbered ID. `TASK-517` is the writer that will use it. No CLI command, no writes.

Decisions:

- The guard runs after `plan_renumbering` returns a nonempty mapping, and before the planner returns. With no candidates it still returns `({}, ())` early, as today.
- "Untouched" tickets are every ticket the plan does not return as writable:
  - every on-disk file the planner already scans (`disk_paths`) that is not in the writable set: unconfigured contexts, and configured files whose `source_of(id)` is not `None`. Parse each with `self._load(context, path, archived)`, which works for an unconfigured `Context` too. Parse errors propagate.
  - every ID in `ticket_ids()` whose `source_of(id)` is not `None`: read it with `self.lookup(id)` and check the returned copy, skipping a `None` result. This covers IDs that have no disk file. Source-selection and read errors propagate; the propagation paths are existing behaviour and get no new test here.
- A link is `frontmatter.parent` or any entry of `frontmatter.depends_on`; `parse` already rejects values that are not task IDs. Add a pure function `blocking_link(frontmatter: Frontmatter, mapping: Mapping[TaskId, TaskId]) -> tuple[TaskId, str] | None` in `src/chitty/renumbering.py`: it returns `(old_id, "parent")` if `TaskId.parse(parent)` is a mapping key, else `(old_id, "depends_on")` for the first `depends_on` entry that is, else `None`. So `task-aaaaaa` matches `TASK-AAAAAA`. Mentions in Description, Notes, History or any other prose never block.
- Scan order: disk files in `disk_paths` order first, then ref-backed IDs in `sorted(...)` `TaskId` order; raise on the first block.
- Links in writable tickets never block: `TASK-517` rewrites those.
- A stale disk copy and its authoritative ref copy are both checked: either one holding a link blocks.
- Read ref-backed tickets only through `lookup`, which applies the source policy (`_choose_source`). That policy has its own tests; this ticket adds none for refs it does not select.
- On the first blocking link raise `ChittyError(f"cannot renumber {old}: {blocking} links to it in {field}")`, where `field` is `parent` or `depends_on`.

Tests: new `tests/test_provisional_link_guard.py`, a `RepoTestCase` with real Git (`git init -b main`, local author, fixtures committed), in the style of `tests/test_provisional_preflight.py`. Each case has one eligible configured provisional `TASK-AAAAAA` in the default `TASK` context and one linking ticket:

- (a) two eligible candidates, `TASK-AAAAAA` and `TASK-BAAAAA`, and an unconfigured context directory `chitty/other/` holding `OTHER-1--x.md` with `depends_on: [TASK-BAAAAA]`, all committed on `main`. Expected message: `cannot renumber TASK-BAAAAA: OTHER-1 links to it in depends_on`.
- (b) a configured `TASK-3` committed on `main` with `parent: task-aaaaaa`, then a branch `task-3` whose commit removes the `parent` line, so the main-checkout file is stale. Assert `source_of(TASK-3) == "task-3"` before planning. Expected message: `cannot renumber TASK-AAAAAA: TASK-3 links to it in parent`.
- (c) a `TASK-3` that exists only on branch `task-3` (committed there, absent from `main` and the working tree), with `depends_on: [TASK-AAAAAA]`. Assert `source_of(TASK-3) == "task-3"`. Expected message: `cannot renumber TASK-AAAAAA: TASK-3 links to it in depends_on`.
- (d) control: as (a), but `OTHER-1` has `depends_on: [TASK-CAAAAA]`, an ID with no ticket that the mapping does not change (a numeric ID would reserve its number and shift the mapping). The plan succeeds.

For (a), (b) and (c), a prose variant replaces the structured link with `See <ID>.` in the Description, where `<ID>` is the same old ID that case links to (`TASK-BAAAAA` in (a), `TASK-AAAAAA` in (b) and (c)).

Property, in `tests/test_property_renumbering.py` with Hypothesis (the repository's property tool): for any mapping of 1 to 4 provisional IDs to numeric IDs, and any frontmatter whose `parent` and `depends_on` are drawn from the mapping keys (each written with random letter case), other IDs not in the mapping, or absent, `blocking_link` returns the parent match when the parent is a key, else the first matching `depends_on` entry, else `None`. Compute the expected result from the drawn values directly. Snapshot HEAD, the index (`git ls-files -s`) and the bytes of every file under `chitty/` after setup, before calling the planner, and compare afterwards. No property: three fixed real-Git placements, each listed here, check which copies are read. The source-selection policy has its own property tests.

Before implementing, run the refusal tests against the unguarded planner and confirm each fails because no error is raised. Then implement, run the new tests and `make check`.

## Acceptance Criteria

- [ ] For each of fixtures (a), (b) and (c), the planner raises `ChittyError` with exactly the expected message given in the Description, and HEAD, index and the snapshotted bytes are unchanged; each refusal test fails on the unguarded planner
- [ ] For each prose variant, and for control (d), the planner returns the mapping `{TASK-AAAAAA: TASK-1, TASK-BAAAAA: TASK-2}` in (a) and (d) and `{TASK-AAAAAA: TASK-4}` in (b) and (c), and a writable set that excludes the linking ticket, with HEAD, index and bytes unchanged
- [ ] `blocking_link`'s property test passes, and fails against a version that compares IDs case-sensitively as strings and against one that ignores `parent`

## History

- 2026-11-21T18:44:38Z eager-ginger-adder → backlog
- 2026-11-21T18:45:12Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:45:12Z eager-ginger-adder backlog → planning
- 2026-11-21T22:58:02Z lively-zinc-newt: changed description
- 2026-11-21T22:58:03Z lively-zinc-newt: changed acceptance criteria
- 2026-11-21T22:58:15Z lively-zinc-newt: changed acceptance criteria
- 2026-11-21T22:58:15Z lively-zinc-newt planning → cold-read
- 2026-11-21T22:59:31Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T22:59:31Z lively-zinc-newt cold-read → planning
- 2026-11-21T22:59:40Z lively-zinc-newt: changed description
- 2026-11-21T22:59:40Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:00:47Z lively-zinc-newt: changed description, acceptance criteria
