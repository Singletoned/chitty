---
title: Refuse renumbering when untouched tickets link to an old ID
status: planning
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
  - every ID in `ticket_ids()` whose `source_of(id)` is not `None`: read it with `self.lookup(id)` and check the returned copy. This covers IDs that have no disk file. Source-selection and read errors propagate.
- A link is `frontmatter.parent` or any entry of `frontmatter.depends_on`. Compare `TaskId.parse(value)` against each old ID in the mapping, so `task-aaaaaa` matches `TASK-AAAAAA`. Mentions in Description, Notes, History or any other prose never block.
- Links in writable tickets never block: `TASK-517` rewrites those.
- A stale disk copy and its authoritative ref copy are both checked: either one holding a link blocks.
- Do not read non-authoritative refs or branches that `ticket_ids()` does not report.
- On the first blocking link raise `ChittyError(f"cannot renumber {old}: {blocking} links to it in {field}")`, where `field` is `parent` or `depends_on`.

Tests: new `tests/test_provisional_link_guard.py`, a `RepoTestCase` with real Git (`git init -b main`, local author, fixtures committed), in the style of `tests/test_provisional_preflight.py`. Each case has one eligible configured provisional `TASK-AAAAAA` in the default `TASK` context and one linking ticket:

- (a) an unconfigured context directory `chitty/other/` holding `OTHER-1--x.md` with `depends_on: [TASK-AAAAAA]`, committed on `main`.
- (b) a configured `TASK-3` committed on `main` with `parent: task-aaaaaa`, then a branch `task-3` whose commit removes the `parent` line, so the main-checkout file is stale. Assert `source_of(TASK-3) == "task-3"` before planning.
- (c) a `TASK-3` that exists only on branch `task-3` (committed there, absent from `main` and the working tree), with `depends_on: [TASK-AAAAAA]`. Assert `source_of(TASK-3) == "task-3"`.

For each, a prose variant replaces the structured link with the text `See TASK-AAAAAA.` in the Description. Snapshot HEAD, the index (`git ls-files -s`) and the bytes of every file under `chitty/` after setup, before calling the planner, and compare afterwards. No property: three fixed real-Git placements, each listed here, check which copies are read. The source-selection policy has its own property tests.

Before implementing, run the refusal tests against the unguarded planner and confirm each fails because no error is raised. Then implement, run the new tests and `make check`.

## Acceptance Criteria

- [ ] Each of the three fixture variants refuses a nonempty plan with an error naming both IDs, and leaves HEAD, index and bytes unchanged. Swap the structured link for a Description mention and the plan succeeds while leaving the same files outside its writable set.

## History

- 2026-11-21T18:44:38Z eager-ginger-adder → backlog
- 2026-11-21T18:45:12Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:45:12Z eager-ginger-adder backlog → planning
- 2026-11-21T22:58:02Z lively-zinc-newt: changed description
