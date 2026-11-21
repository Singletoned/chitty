---
title: Renumber provisional tickets in `Repo.renumber_provisional`
status: todo
depends_on:
  - TASK-381
  - TASK-389
  - TASK-378
  - TASK-507
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` and `provisional: true` (`TASK-380`, `TASK-389`). Once it reaches `main` it should get an ordinary sequential number. This is cosmetic and idempotent. This ticket builds the store method; `TASK-392` wires it to the CLI.

Starts after `TASK-381` (`plan_renumbering`, `replace_ids`) and `TASK-389` land.

Decisions:

- New `Repo.renumber_provisional() -> tuple[Change, ...]` in `src/chitty/store.py`, returning one `Change` per renumbered ticket (empty when none).
- It acts only "on `main`": outside a Git repository (`git.is_repository` false), or in one where a fresh `git.current_branch(self.root)` (not `Repo._current_branch()`, which caches) equals `Repo._main_branch()` (the configured main branch). Check `git.is_repository` first: inside a repository, `current_branch` returning `None` means a detached `HEAD`. Off `main`, including a detached `HEAD`, it raises `ProvisionalOffMain`, a new `ChittyError` subclass in `src/chitty/errors.py`, saying provisional tickets are renumbered on main; the CLI turns that into a no-op (`TASK-392`).
- It works on this checkout's ticket files on disk in the active and archive directories of every configured context (`self.contexts()`). Decided 2026-11-21: directories under `chitty/` that are not configured (which `discovered_contexts()` also finds) are left alone, since they have no allocation policy and `_all_or_nothing` does not snapshot them; their mentions of old IDs dangle, accepted. It but skips every file whose ticket `Repo` reads from another ref (`StoredTask.branch` is not `None`, after `TASK-378`): the main checkout also holds `main`'s stale copies of in-flight tickets, and writing them would make the ticket change on both sides. Such tickets, and tickets only on other branches, keep their mentions of the old ID (dangling; accepted).
- First parse every ticket file and plan everything, so an unparseable file fails before any write. The planned set is the provisional tickets in on-disk files that are not skipped (see above). The used numbers come from `_used_numbers` over every on-disk file, skipped ones included, so a skipped in-flight ticket's number is never reused. Decided 2026-11-21: also reserve, for each sequential context, the integer numbers of every reference with that context's prefix that any on-disk ticket file mentions, found with `ids.ticket_references(text, prefixes)` over each file's text (skip references whose number is a string, such as provisional IDs). Then every allocated number is unmentioned, which `rewrite_task`'s fresh-target contract (`TASK-507`) requires: a dangling `TASK-4` mention means the first provisional ticket gets `TASK-5`. Before calling `plan_renumbering`, group the planned files by provisional ID; if two files share one, raise `ChittyError` naming both paths and write nothing (`plan_renumbering`'s own `duplicate provisional task ID` message has no paths; `chitty renumber PATH` then separates them). If the store's own `is used by more than one file` error, which already names both paths, is raised first, let it propagate.
- Extract `Repo._used_numbers(context) -> set[int]` from `next_number`, keeping everything `next_number` counts (active and archive files, and `_deleted_numbers` in delete mode); `next_number` then returns `ids.next_number` of it for sequential contexts, its random branch unchanged. Pass them to `plan_renumbering` keyed by prefix (`Mapping[str, set[int]]`): `{context.prefix: _used_numbers(context)}` over sequential contexts, taking the union where contexts share a prefix. A provisional ticket in a `random_ids` context is left alone.
- For each renumbered ticket: a new helper (do not change `_relocate`, which `move` and `renumber PATH` share) moves the file to the new ID in the same directory (active or archive), with the slug of its final title, as `check.fix` would name it, removes `provisional`, sets `moved_from` to the provisional ID (replacing any earlier value), and adds a History event `renumbered from <old ID>`.
- Decided 2026-11-21: every written file's final path uses `ids.filename(<final ID>, ids.slugify(<final title>))`, so `_commit`'s `check.fix` has nothing to rename and the commit's paths stay right. A ticket whose title mentions a renumbered ID is therefore renamed too (old path removed, new path in the commit).
- Rewrite mentions in every on-disk ticket file that is not skipped, provisional or not, with `rewrite_task(task, mapping)` from `src/chitty/renumbering.py` (`TASK-507`, which lands first). `moved_from` is not rewritten, so a renumbered file's own `moved_from` and History keep the provisional ID.
- Order: `_prepare_write()` first. Then compute every affected file's final `Task` and path in memory (a renamed ticket's rewrites applied to its renamed content), and inside `with self._all_or_nothing():`, as `add`, `edit` and `archive_done` use it, write each file once at its final path with `_write(path, task.render())`, as `_relocate` does (not `_save`, which applies the current-version guard and dependency checks), remove old paths, and make one `_commit(change, "renumber provisional tickets")` whose `Task:` trailers name every renamed and rewritten ticket, as `archive_done` batches. `_all_or_nothing` takes the main checkout lock and, on any exception (including `chitty fix` validation, formatting, or `autocommit failed`), restores the ticket files and the Git index and re-raises; do not reimplement it. Outside a Git repository, `_prepare_write()` keeps its existing policy (`tests/test_autocommit_requires_git.py`): with `autocommit = true` it refuses, as every write does; with `autocommit = false` the files are written and no commit is made.

Tests: real-file tests calling `Repo.renumber_provisional()` in a new `tests/test_renumber_provisional.py`, inheriting `RepoTestCase` from `tests/support.py`, running `git init -b main`, setting `user.name` and `user.email` as `tests/test_autocommit.py` does, and `autocommit = true` (its default config has `autocommit = false`). Patch the provisional draw (`_provisional_draw`, `TASK-389`) in the real-file tests so the suffixes are known: `mock.patch("chitty.store._provisional_draw", side_effect=[0] * 6 + [1] + [0] * 5)` around the two `add` calls gives `TASK-AAAAAA` and then `TASK-BAAAAA` (each suffix takes six draws: one letter, then five characters from letters and digits). `AAAAAA` sorts first, so it becomes `TASK-4` and `BAAAAA` becomes `TASK-5`. Make provisional tickets with `chitty add` on a branch (archive the `TASK-AAAAAA` one there), `git switch main`, `git merge` the branch, and stay on `main`. No property here: file plumbing over the cases in the criteria (the `rewrite_task` property is `TASK-507`).

## Acceptance Criteria

- [ ] On `main`, with `TASK-3` the highest number, an active and an archived provisional ticket (the second depending on the first), and `TASK-3` itself listing one in `depends_on` and mentioning both in its Description: the provisional tickets get `TASK-4` and `TASK-5` in ascending order of their provisional suffixes; both files are moved in their own directories, lose `provisional`, and have `moved_from` set to their provisional IDs; the second's `depends_on` names the first's new ID; `TASK-3`'s `depends_on` and Description are rewritten and its History is not; one commit names all three in `Task:` trailers; a variant with `TASK-3` archived (so the highest number is only in the archive) still gives `TASK-4` and `TASK-5`; and a variant creating them in reverse order (`side_effect=[1] + [0] * 5 + [0] * 6`, so `TASK-BAAAAA` is made first) gives the same result, because the order comes from the IDs, not from file listing; with `archive = "delete"` in `chitty.toml` and a `chitty/tasks/TASK-4--gone.md` file committed, then removed with `git rm` and that removal committed (`_deleted_numbers` reads `git.deleted_paths`, so it then reports 4), the provisional tickets become `TASK-5` and `TASK-6`
- [ ] A second call returns no changes and makes no commit; off `main` and on a detached `HEAD` it raises `ChittyError` and changes nothing; a provisional ticket in a context with `random_ids = true` keeps its ID and bytes while a sequential context's provisional ticket in the same call is renumbered; a provisional `chitty/other/TASK-BBBBBB--x.md` in an unconfigured directory, and a file there mentioning a renumbered ID, both keep their bytes
- [ ] With a `.git/hooks/pre-commit` that exits 1, the call raises `ChittyError` containing `autocommit failed`, and `git status --porcelain` and every ticket file's bytes equal what they were before; with a ticket file planted in `chitty/tasks/` under a valid name but unparseable content, it raises `ChittyError` naming that file, and every ticket file's bytes and `git status --porcelain` equal their values before the call; with two files sharing one provisional ID, it raises a `ChittyError` whose message names both paths (either this method's error or the store's `is used by more than one file`), and every ticket file's bytes and `git status --porcelain` equal their values before the call
- [ ] Outside a Git repository (a temporary directory initialised with `chitty init`, then `autocommit = false` set in its `chitty.toml`, so `chitty_version` is current, and a file `chitty/tasks/TASK-AAAAAA--x.md` with `provisional: true`), the call renumbers it to `TASK-1` without error, and no `.git` directory is created. On `main`, with `TASK-3` titled `After TASK-AAAAAA`, depending on the provisional `TASK-AAAAAA`, and mentioning a dangling `TASK-4` (no such file) in its Description: the provisional ticket becomes `TASK-5`; `TASK-3`'s `depends_on` becomes `[TASK-5]`, its Description still mentions `TASK-4`, and its file becomes `chitty/tasks/TASK-3--after-task-5.md` (the old file is gone, and the commit includes both paths). `make check` passes
- [ ] `TASK-3`, the highest-numbered ticket, is in flight on branch `task-3` (one commit ahead of `main` that changes `TASK-3`'s file, so `Repo.find(TaskId.parse("TASK-3")).branch == "task-3"`, which the test asserts first) while its `main` copy mentions a provisional ID: its `main` file is left byte-identical, the two provisional tickets on `main` still become `TASK-4` and `TASK-5` (the skipped ticket's number counts as used), and the commit's `Task:` trailers name those tickets and not `TASK-3`

## Plan

Extract used-number collection, parse and select on-disk tickets, reserve mentioned numbers, then plan and atomically write renames and rewrites in one commit. Cover the specified Git, archive, rollback, source-selection and standalone cases with real-file tests.

## Notes

The requested rewrite and property cannot be implemented as written against the current model: `src/chitty/model.py` `_split_sections` rejects any non-whitespace content before the first `##` section, so a parsed `Task` cannot contain an ID in the preamble. The description nevertheless requires rewriting that text and generating tickets with mentions in every field and section; frontmatter fields such as `status`, `created` and `provisional` also cannot contain such mentions, while `moved_from` and History are explicitly excluded from rewriting. Please specify whether to change the parser to allow preamble content or remove that requirement, and clarify the property fixture to identify the eligible fields and sections. No implementation was started; regression evidence and verification remain outstanding.

Planner 2026-11-21: dropped the pre-section text from the rewrite, since the parser rejects any content before the first `##` section. The property now names exactly where mentions are generated: `title`, `depends_on`, `parent` and the sections. No other frontmatter field is rewritten.

Planner 2026-11-21, after two cold reads: split the pure `rewrite_task` and its property into `TASK-507` (lands first). Here: the archived provisional ticket is named and an archived-highest variant added; the planned set and used numbers are defined; duplicate paths are reported by this method; no commit outside Git, with a criterion. The branch-only clause in criterion 2 is dropped, because criterion 5 tests skipping.

Planner 2026-11-21, after the cold read: criterion 5 now shows a skipped ticket's number is never reused; a reverse-creation variant; unchanged-bytes checks for the parse and duplicate errors. The `TASK-507` dependency is gated by `depends_on`.

Two unresolved conflicts prevent implementing the specified method safely:

1. The required first call to `Repo._prepare_write()` rejects any non-Git directory when `autocommit = true` (and also rejects a missing Git executable), whereas criterion 4 requires that exact configuration to succeed outside Git. This is an existing, tested policy in `tests/test_autocommit_requires_git.py`. Decide how this operation is exempted while other writes retain their policy, including what happens with a stale setup and without the Git executable; specify the corresponding tests. Calling `_prepare_write()` unchanged cannot satisfy criterion 4.
2. `rewrite_task` from `TASK-507` requires callers to guarantee that mapping targets are not mentioned in the input ticket. This ticket allocates using filenames and deleted numbers only, so it cannot guarantee that: an on-disk ticket may already mention dangling `TASK-4`, or depend on both `TASK-4` and `TASK-AAAAAA`, when the latter is allocated `TASK-4`. Rewriting the dependencies then produces duplicate values rejected by the model. Decide whether to reserve mentioned numbers, reject such cases before writing, or change the rewrite contract, and specify fixture, action and assertions for the chosen behavior.

Rebased this worktree onto `main` to obtain the landed `TASK-507` dependency. No implementation or tests were written; regression evidence and verification remain outstanding.

Planner 2026-11-21: outside Git the existing autocommit policy stands, and criterion 4 now uses `autocommit = false`. Mentioned numbers are reserved, so targets are always fresh; added the dangling `TASK-4` case.

Planner 2026-11-21, after the cold read: every non-skipped on-disk file is rewritten; writes go through `_all_or_nothing`, which already restores files and the index and takes the lock; the main-branch check uses a fresh `git.current_branch`; reserved numbers are the integer numbers of matching-prefix references.

Two conflicts with the required existing finalization prevent implementation:

1. Criterion 4 requires an autocommitted rewrite of `TASK-3` retaining a dangling `TASK-4` dependency. `_commit` calls `check.fix`, whose `check` reports `depends_on TASK-4: no such task` as an error; `_commit` then raises and `_all_or_nothing` rolls back. Decide whether this case should allow dangling dependencies during finalization, change the fixture, or change the required finalization, and specify the corresponding test.
2. The description requires keeping the same filename slug while rewriting mentions in every eligible title. When a rewritten title contains an old ID and `autocommit` or `autoformat` is enabled, `_commit` calls `check.fix`, which renames the file to the slug of the rewritten title. This conflicts with the same-slug requirement and can also leave the planned commit paths stale. Decide which filename rule applies and specify a title-reference fixture, action and assertions covering finalization.

No implementation or tests were written. Regression evidence and verification remain outstanding.

Planner 2026-11-21, after the worker's return: the dangling `TASK-4` is now a Description mention, since `check` rejects a dangling `depends_on` at commit. Final paths use the final title's slug, so `fix` renames nothing; criterion 4 covers a title mention.

Planner 2026-11-21, after the cold read: the outside-Git fixture uses `chitty init`; delete mode and `random_ids` contexts are now covered in criteria 1 and 2; criterion 5 asserts the branch source first; either duplicate-path error is accepted. Not taken: a property over reserved numbers (a set union over `ticket_references`; allocation is covered by `TASK-381`'s property).

The requirement to rewrite on-disk ticket files in every context conflicts with the required rollback mechanism for unconfigured on-disk contexts. `Repo.discovered_contexts()` includes directories absent from configuration, but `_all_or_nothing()` snapshots and restores only `self.contexts()` (configured contexts). If an eligible ticket in an unconfigured directory is rewritten and the pre-commit hook fails, its bytes remain changed despite the promised full rollback. Such a context also has no `random_ids` configuration for deciding whether its provisional tickets are eligible. Please decide whether unconfigured contexts are excluded or supported, and if supported specify their allocation policy and extend the rollback mechanism; specify a real-file fixture, action and assertions covering an unconfigured context and rollback. The current criteria do not test this case. No code or tests were written; regression evidence and verification remain outstanding.

Planner 2026-11-21: only configured contexts are renumbered or rewritten; unconfigured directories are left alone (guard in criterion 2).

## History

- 2026-11-18T16:34:15Z lively-quartz-crane → backlog
- 2026-11-18T16:34:50Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:34:50Z lively-quartz-crane backlog → planning
- 2026-11-18T16:35:13Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:37:35Z lively-quartz-crane: changed title, description, acceptance criteria
- 2026-11-18T16:37:35Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:37:37Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:40:38Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:46:06Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:46:06Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:48:24Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:50:43Z lively-quartz-crane: changed description
- 2026-11-18T17:50:43Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:50:45Z lively-quartz-crane planning → todo
- 2026-11-18T17:50:53Z lively-quartz-crane: changed description
- 2026-11-18T17:53:03Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:53:03Z lively-quartz-crane todo → planning
- 2026-11-18T17:53:05Z lively-quartz-crane planning → todo
- 2026-11-21T13:00:34Z mellow-teal-urchin todo → doing
- 2026-11-21T13:03:53Z mellow-teal-urchin: changed owner, notes
- 2026-11-21T13:03:53Z mellow-teal-urchin doing → planning
- 2026-11-21T13:05:20Z sunny-ebony-kestrel: changed description, notes
- 2026-11-21T13:05:20Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:07:19Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:07:46Z sunny-ebony-kestrel: changed description
- 2026-11-21T13:10:46Z sunny-ebony-kestrel: changed dependencies, description, acceptance criteria, notes
- 2026-11-21T13:10:46Z sunny-ebony-kestrel cold-read → planning
- 2026-11-21T13:17:52Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:19:05Z sunny-ebony-kestrel: changed acceptance criteria, notes
- 2026-11-21T13:19:05Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T14:26:11Z daring-yellow-gannet todo → doing
- 2026-11-21T14:28:21Z daring-yellow-gannet: changed owner, notes
- 2026-11-21T14:28:21Z daring-yellow-gannet doing → planning
- 2026-11-21T14:29:29Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T14:29:29Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T14:33:28Z sunny-ebony-kestrel: changed description, notes
- 2026-11-21T14:33:28Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T14:33:43Z witty-maroon-newt todo → doing
- 2026-11-21T14:35:24Z witty-maroon-newt: wrote the plan
- 2026-11-21T14:35:54Z witty-maroon-newt: changed owner, notes
- 2026-11-21T14:35:54Z witty-maroon-newt doing → planning
- 2026-11-21T14:37:10Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T14:37:10Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T14:38:46Z sunny-ebony-kestrel: changed acceptance criteria, notes
- 2026-11-21T14:38:46Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T14:39:04Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T14:42:34Z upbeat-navy-toad todo → doing
- 2026-11-21T14:45:08Z upbeat-navy-toad: changed owner, notes
- 2026-11-21T14:45:08Z upbeat-navy-toad doing → planning
- 2026-11-21T14:45:40Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T14:45:40Z sunny-ebony-kestrel planning → todo
