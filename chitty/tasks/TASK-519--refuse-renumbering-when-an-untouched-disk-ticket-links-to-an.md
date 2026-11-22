---
title: Refuse renumbering when an untouched disk ticket links to an old ID
status: doing
depends_on:
  - TASK-391
  - TASK-526
parent: TASK-391
created: 2026-11-21
---

## Description

Extend the read-only planner `Repo._plan_provisional_renumbering` in `src/chitty/store.py` (landed by `TASK-391`) so it refuses a plan that would leave a structured link pointing at a renumbered ID. `TASK-517` is the writer that will use it. No CLI command, no writes.

Decisions:

- The guard runs after `plan_renumbering` returns a nonempty mapping, and before the planner returns. With no candidates it still returns `({}, ())` early, as today.
- "Untouched" tickets are every ticket the plan does not return as writable:
  - every on-disk file the planner already scans (`disk_paths`) that is not in the writable set: unconfigured contexts, and configured files whose `source_of(id)` is not `None`. Parse each with `self._load(context, path, archived)`, which works for an unconfigured `Context` too. Parse errors propagate.
  - ticket copies read from refs are `TASK-536` (split 2026-11-22); this ticket scans disk files only.
- A link is `frontmatter.parent` or any entry of `frontmatter.depends_on`; `parse` already rejects values that are not task IDs. Use `blocking_link(frontmatter, mapping)` from `src/chitty/renumbering.py` (`TASK-526`), which returns `(old_id, field)` or `None`. So `task-aaaaaa` matches `TASK-AAAAAA`. Mentions in Description, Notes, History or any other prose never block.
- Scan order: disk files in `disk_paths` order; raise on the first block. Put the disk scan in its own helper method so `TASK-536` can add the ref scan after it.
- Links in writable tickets never block: `TASK-517` rewrites those.
- A stale disk copy is checked even though its authoritative copy is on a ref (fixture (b)); the ref copy itself is `TASK-536`.
- On the first blocking link raise `ChittyError(f"cannot renumber {old}: {blocking} links to it in {field}")`, where `field` is `parent` or `depends_on`.

Tests: new `tests/test_provisional_link_guard.py`, a `RepoTestCase` with real Git (`git init -b main`, local author, fixtures committed), in the style of `tests/test_provisional_preflight.py`. Keep the `chitty.toml` that `RepoTestCase` writes, so the `TASK` context is sequential. Each case has an eligible candidate `chitty/tasks/TASK-AAAAAA--example.md` whose frontmatter has `provisional: true`, and one linking ticket. "Writable set" below means the paths of the returned `StoredTask`s; the guard tells untouched disk files apart by path.

- (a) two eligible candidates, `TASK-AAAAAA` and `TASK-BAAAAA`, and an unconfigured context directory `chitty/other/` holding `OTHER-1--x.md` with `depends_on: [TASK-BAAAAA]`, all committed on `main`. Expected message: `cannot renumber TASK-BAAAAA: OTHER-1 links to it in depends_on`.
- (b) a configured `TASK-3` committed on `main` with `parent: task-aaaaaa`, then a branch `task-3` whose commit removes the `parent` line, so the main-checkout file is stale. Assert `source_of(TASK-3) == "task-3"` before planning. Expected message: `cannot renumber TASK-AAAAAA: TASK-3 links to it in parent`.
- (d) control: as (a), but `OTHER-1` has `depends_on: [TASK-CAAAAA]`, an ID with no ticket that the mapping does not change (a numeric ID would reserve its number and shift the mapping). The plan succeeds.

For (a) and (b), a prose variant replaces the structured link with `See <ID>.` in the Description of the same copy that held the link (in (b), the main copy), where `<ID>` is the old ID that case links to (`TASK-BAAAAA` in (a), `TASK-AAAAAA` in (b)).

For every planner fixture, snapshot HEAD, the index (`git ls-files -s`) and the bytes of every file under `chitty/` (`rglob("*")`, not only `*.md`) after setup, before calling the planner, and compare afterwards. Fixtures (a), (b) and (d) are example tests, not properties: each covers one fixed placement (unconfigured disk file, stale disk copy, control), and the source-selection policy has its own property tests.

The comparison itself has its property tests in `TASK-526`.

Before implementing, run the refusal tests against the unguarded planner and confirm each fails because no error is raised. Then implement, run the new tests and `make check`.

## Acceptance Criteria

- [ ] For each of fixtures (a) and (b), the planner raises `ChittyError` whose `str()` equals the expected message given in the Description (`assertEqual`), and HEAD, index and the snapshotted bytes are unchanged; each refusal test fails on the unguarded planner
- [ ] For the prose variants of (a) and (b), and for control (d), the planner returns `{TASK-AAAAAA: TASK-1, TASK-BAAAAA: TASK-2}` in (a) and (d) and `{TASK-AAAAAA: TASK-4}` in (b), and a writable set that excludes the linking ticket, with HEAD, index and bytes unchanged

## Plan

Add disk-only Git fixtures and confirm refusal tests fail; implement a path-based untouched disk scan with blocking_link, then format and check.

## Notes

Runner error (agent): TASK-519 was unchanged; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-519`

Split 2026-11-21: the worker model returned five sessions saying it could not finish in one response, with no code. `blocking_link` and its property moved to `TASK-526`. Keep this in planning until `TASK-526` lands; then check the landed signature, cold-read and move to `todo`.

Rebased onto `main` 2026-11-21 after `TASK-526` landed `blocking_link` (signature as specified) and `TASK-520` landed the branch guard.

Runner error (agent): TASK-519 was unchanged; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-519`

Split again 2026-11-22: the worker model gave up a second time (six sessions, no code). Ref-backed copies, fixtures (c) and (e), moved to `TASK-536`.

Both refusal tests failed against the unguarded planner with ChittyError not raised.

## Summary

Added disk link guard and real Git regression fixtures. Both refusal tests failed before the fix; make check passed.

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
- 2026-11-21T23:02:43Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:02:43Z lively-zinc-newt cold-read → todo
- 2026-11-21T23:04:21Z able-hazel-newt todo → doing
- 2026-11-21T23:05:50Z able-hazel-newt: wrote the plan
- 2026-11-21T23:06:53Z able-hazel-newt: changed notes
- 2026-11-21T23:06:53Z able-hazel-newt doing → error
- 2026-11-21T23:15:49Z lively-zinc-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-21T23:15:49Z lively-zinc-newt error → planning
- 2026-11-22T00:07:19Z lively-zinc-newt: changed notes
- 2026-11-22T00:07:19Z lively-zinc-newt planning → cold-read
- 2026-11-22T00:09:08Z lively-zinc-newt: changed description, acceptance criteria; wrote the plan
- 2026-11-22T00:09:08Z lively-zinc-newt cold-read → todo
- 2026-11-22T00:11:51Z friendly-white-toad todo → doing
- 2026-11-22T00:14:04Z friendly-white-toad: wrote the plan
- 2026-11-22T00:15:32Z friendly-white-toad: changed notes
- 2026-11-22T00:15:32Z friendly-white-toad doing → error
- 2026-11-22T00:16:37Z lively-zinc-newt: changed title, description, acceptance criteria, notes
- 2026-11-22T00:16:37Z lively-zinc-newt error → todo
- 2026-11-22T00:21:28Z eager-bronze-raven todo → doing
- 2026-11-22T00:23:34Z eager-bronze-raven: wrote the plan
- 2026-11-22T00:24:26Z eager-bronze-raven: changed notes
- 2026-11-22T00:26:08Z eager-bronze-raven: changed summary
