---
title: Prepare the files of a provisional renumbering in memory
status: doing
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-517` on 2026-11-22. `TASK-517` will write a provisional renumbering in one commit. This ticket adds the in-memory step it uses: from the read-only plan, compute every changed ticket's final text and path. It writes nothing.

Add `Repo._prepare_renumbering(mapping: dict[TaskId, TaskId], writable: tuple[StoredTask, ...]) -> list[tuple[StoredTask, Task, Path]]` in `src/chitty/store.py`, returning `(original, final_task, final_path)` for each writable ticket whose text or path changes, in `writable` order. For each writable ticket:

- `final = rewrite_task(stored.task, mapping)` (`src/chitty/renumbering.py`).
- If `stored.id` is a mapping key (a renumbered ticket): drop `provisional`, set `moved_from` to the old ID, and append a History event `renumbered from <old ID>` with `final.with_history_event(datetime.now(UTC), actor(), ...)`, as `src/chitty/import_backlog.py` (near line 236) does (not `with_history`, which records status changes). Other tickets keep `moved_from` and History as they are.
- Final ID: `mapping.get(stored.id, stored.id)`. Final path: when the ID or the title changed, the same directory as `stored.path` with file name `ids.filename(final_id, ids.slugify(final.frontmatter.title))`, computed from the rewritten title; otherwise `stored.path` unchanged (decided 2026-11-22: never rename a ticket just because its existing slug differs from its title).
- Skip a ticket whose final text and path both equal the original.

Rechecked on `main` 2026-11-22: `_plan_provisional_renumbering`, `rewrite_task`, `Task.with_history_event(when, actor, action)`, `ids.filename(task_id, slug)` and `ids.slugify(title)` exist with these shapes.

Test in a new `tests/test_renumber_provisional.py`, `RepoTestCase`, real files and real Git on `main` (`git init -b main`, local author), fixture committed: files `chitty/tasks/archive/TASK-AAAAAA--alpha.md` (provisional, title `Alpha`), `chitty/tasks/TASK-BAAAAA--beta.md` (provisional, title `Beta`) with `depends_on: [TASK-AAAAAA]`; `chitty/tasks/TASK-3--after-task-aaaaaa.md` (title `After TASK-AAAAAA`), with `depends_on: [TASK-BAAAAA]`, a Description mentioning `TASK-AAAAAA`, `TASK-BAAAAA` and a dangling `TASK-4`, and an existing History entry mentioning `TASK-AAAAAA`; and an untouched `chitty/human/HUMAN-1--old-name.md` titled `Human one` (its slug deliberately differs from its title; it must get no entry). Set `CHITTY_ACTOR` for the test (`mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"})`), because `RepoTestCase` clears it and `actor()` raises without it. Call `_plan_provisional_renumbering()`, then `_prepare_renumbering(...)`, and assert: the mapping is `TASK-AAAAAA -> TASK-5`, `TASK-BAAAAA -> TASK-6` (a cold reader's probe confirmed this, with `TASK-4` reserved by the mention); exactly three entries, none for `HUMAN-1`; final paths `chitty/tasks/archive/TASK-5--alpha.md`, `chitty/tasks/TASK-6--beta.md` and `chitty/tasks/TASK-3--after-task-5.md`; dependencies and Description name the new IDs except the dangling `TASK-4`; both renumbered tickets have `provisional` unset, `moved_from` equal to their old ID, and a last History event ending `renumbered from <old ID>`; `TASK-3`'s earlier History entries are unchanged; and no file under `chitty/` changed bytes. No property: `TASK-507` covers the pure rewrite and `TASK-381` the allocation.

## Acceptance Criteria

- [ ] The prepare test passes and fails against a `NotImplementedError` stub; `make check` passes

## Plan

Strengthen the History assertion to check the final event ends with the required action; verify against a stub and run the required checks.

## Notes

The preparation regression test failed against a NotImplementedError stub before implementation.

Review failed (tests): The new test does not verify the specified last History event. This is a newly discovered finding.
1: fail - The test uses assertIn for the renumbering text, so an earlier event or a last event with extra trailing text would pass; assert that the last History event ends with the specified action for each renumbered ticket. `.venv/bin/python -m unittest tests.test_renumber_provisional` printed OK; replacing the helper at runtime with a NotImplementedError stub printed FAILED (errors=1); `make check` printed OK for 1090 tests.

## Summary

Implemented in-memory preparation and real Git regression coverage. The test failed with a NotImplementedError stub and passes with the implementation; make check passes.

## History

- 2026-11-22T01:37:46Z lively-zinc-newt → cold-read
- 2026-11-22T01:38:01Z lively-zinc-newt: changed description
- 2026-11-22T01:39:13Z lively-zinc-newt: changed description
- 2026-11-22T01:39:13Z lively-zinc-newt cold-read → todo
- 2026-11-22T02:31:37Z nimble-hazel-raven todo → doing
- 2026-11-22T02:33:57Z nimble-hazel-raven: wrote the plan
- 2026-11-22T02:35:18Z nimble-hazel-raven: changed notes
- 2026-11-22T02:37:37Z nimble-hazel-raven: changed summary
- 2026-11-22T02:39:07Z nimble-hazel-raven doing → review
- 2026-11-22T02:43:29Z calm-lilac-lapwing: changed acceptance criteria, notes
- 2026-11-22T02:43:29Z calm-lilac-lapwing review → doing
- 2026-11-22T02:50:17Z nimble-silver-toad: wrote the plan
