---
title: Prepare the files of a provisional renumbering in memory
status: cold-read
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-517` on 2026-11-22. `TASK-517` will write a provisional renumbering in one commit. This ticket adds the in-memory step it uses: from the read-only plan, compute every changed ticket's final text and path. It writes nothing.

Add `Repo._prepare_renumbering(mapping: dict[TaskId, TaskId], writable: tuple[StoredTask, ...]) -> list[tuple[StoredTask, Task, Path]]` in `src/chitty/store.py`, returning `(original, final_task, final_path)` for each writable ticket whose text or path changes, in `writable` order. For each writable ticket:

- `final = rewrite_task(stored.task, mapping)` (`src/chitty/renumbering.py`).
- If `stored.id` is a mapping key (a renumbered ticket): drop `provisional`, set `moved_from` to the old ID, and append a History event `renumbered from <old ID>` with `final.with_history_event(datetime.now(UTC), actor(), ...)`, as `_set_archived` does. Other tickets keep `moved_from` and History as they are.
- Final ID: `mapping.get(stored.id, stored.id)`. Final path: the same directory as `stored.path`, file name `ids.filename(final_id, ids.slugify(final.frontmatter.title))`, computed from the rewritten title.
- Skip a ticket whose final text and path both equal the original.

Rechecked on `main` 2026-11-22: `_plan_provisional_renumbering`, `rewrite_task`, `Task.with_history_event(when, actor, action)`, `ids.filename(task_id, slug)` and `ids.slugify(title)` exist with these shapes.

Test in a new `tests/test_renumber_provisional.py`, `RepoTestCase`, real files and real Git on `main` (`git init -b main`, local author), fixture committed: an archived provisional `TASK-AAAAAA`; an active provisional `TASK-BAAAAA` with `depends_on: [TASK-AAAAAA]`; an active `TASK-3` titled `After TASK-AAAAAA`, with `depends_on: [TASK-BAAAAA]`, a Description mentioning `TASK-AAAAAA`, `TASK-BAAAAA` and a dangling `TASK-4`, and an existing History entry mentioning `TASK-AAAAAA`; and an untouched `HUMAN-1` in the `human` context. Call `_plan_provisional_renumbering()`, then `_prepare_renumbering(...)`, and assert: the mapping is `TASK-AAAAAA -> TASK-5`, `TASK-BAAAAA -> TASK-6` (a cold reader's probe confirmed this, with `TASK-4` reserved by the mention); exactly three entries, none for `HUMAN-1`; final paths `chitty/tasks/archive/TASK-5--example.md` (or whatever slug its title gives), `chitty/tasks/TASK-6--...` and `chitty/tasks/TASK-3--after-task-5.md`; dependencies and Description name the new IDs except the dangling `TASK-4`; both renumbered tickets have `provisional` unset, `moved_from` equal to their old ID, and a last History event ending `renumbered from <old ID>`; `TASK-3`'s earlier History entries are unchanged; and no file under `chitty/` changed bytes. Write the fixture's titles so the expected slugs are fixed in the test. No property: `TASK-507` covers the pure rewrite and `TASK-381` the allocation.

## Acceptance Criteria

- [ ] The prepare test passes and fails against a `NotImplementedError` stub; `make check` passes

## History

- 2026-11-22T01:37:46Z lively-zinc-newt → cold-read
