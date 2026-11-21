---
title: Renumber provisional tickets in `Repo.renumber_provisional`
status: doing
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
- It works on this checkout's ticket files on disk (active and archive directories of every context), but skips every file whose ticket `Repo` reads from another ref (`StoredTask.branch` is not `None`, after `TASK-378`): the main checkout also holds `main`'s stale copies of in-flight tickets, and writing them would make the ticket change on both sides. Such tickets, and tickets only on other branches, keep their mentions of the old ID (dangling; accepted).
- First parse every ticket file and plan everything, so an unparseable file fails before any write. The planned set is the provisional tickets in on-disk files that are not skipped (see above). The used numbers come from `_used_numbers` over every on-disk file, skipped ones included, so a skipped in-flight ticket's number is never reused. Decided 2026-11-21: also reserve, for each sequential context, the integer numbers of every reference with that context's prefix that any on-disk ticket file mentions, found with `ids.ticket_references(text, prefixes)` over each file's text (skip references whose number is a string, such as provisional IDs). Then every allocated number is unmentioned, which `rewrite_task`'s fresh-target contract (`TASK-507`) requires: a dangling `TASK-4` mention means the first provisional ticket gets `TASK-5`. Before calling `plan_renumbering`, group the planned files by provisional ID; if two files share one, raise `ChittyError` naming both paths and write nothing (`plan_renumbering`'s own `duplicate provisional task ID` message has no paths; `chitty renumber PATH` then separates them). If the store's own `is used by more than one file` error, which already names both paths, is raised first, let it propagate.
- Extract `Repo._used_numbers(context) -> set[int]` from `next_number`, keeping everything `next_number` counts (active and archive files, and `_deleted_numbers` in delete mode); `next_number` then returns `ids.next_number` of it for sequential contexts, its random branch unchanged. Pass them to `plan_renumbering` keyed by prefix (`Mapping[str, set[int]]`): `{context.prefix: _used_numbers(context)}` over sequential contexts, taking the union where contexts share a prefix. A provisional ticket in a `random_ids` context is left alone.
- For each renumbered ticket: a new helper (do not change `_relocate`, which `move` and `renumber PATH` share) moves the file to the new ID with the same slug in the same directory (active or archive), removes `provisional`, sets `moved_from` to the provisional ID (replacing any earlier value), and adds a History event `renumbered from <old ID>`.
- Rewrite mentions in every on-disk ticket file that is not skipped, provisional or not, with `rewrite_task(task, mapping)` from `src/chitty/renumbering.py` (`TASK-507`, which lands first). `moved_from` is not rewritten, so a renumbered file's own `moved_from` and History keep the provisional ID.
- Order: `_prepare_write()` first. Then compute every affected file's final `Task` and path in memory (a renamed ticket's rewrites applied to its renamed content), and inside `with self._all_or_nothing():`, as `add`, `edit` and `archive_done` use it, write each file once at its final path with `_write(path, task.render())`, as `_relocate` does (not `_save`, which applies the current-version guard and dependency checks), remove old paths, and make one `_commit(change, "renumber provisional tickets")` whose `Task:` trailers name every renamed and rewritten ticket, as `archive_done` batches. `_all_or_nothing` takes the main checkout lock and, on any exception (including `chitty fix` validation, formatting, or `autocommit failed`), restores the ticket files and the Git index and re-raises; do not reimplement it. Outside a Git repository, `_prepare_write()` keeps its existing policy (`tests/test_autocommit_requires_git.py`): with `autocommit = true` it refuses, as every write does; with `autocommit = false` the files are written and no commit is made.

Tests: real-file tests calling `Repo.renumber_provisional()` in a new `tests/test_renumber_provisional.py`, inheriting `RepoTestCase` from `tests/support.py`, running `git init -b main`, setting `user.name` and `user.email` as `tests/test_autocommit.py` does, and `autocommit = true` (its default config has `autocommit = false`). Patch the provisional draw (`_provisional_draw`, `TASK-389`) in the real-file tests so the suffixes are known: `mock.patch("chitty.store._provisional_draw", side_effect=[0] * 6 + [1] + [0] * 5)` around the two `add` calls gives `TASK-AAAAAA` and then `TASK-BAAAAA` (each suffix takes six draws: one letter, then five characters from letters and digits). `AAAAAA` sorts first, so it becomes `TASK-4` and `BAAAAA` becomes `TASK-5`. Make provisional tickets with `chitty add` on a branch (archive the `TASK-AAAAAA` one there), `git switch main`, `git merge` the branch, and stay on `main`. No property here: file plumbing over the cases in the criteria (the `rewrite_task` property is `TASK-507`).

## Acceptance Criteria

- [ ] On `main`, with `TASK-3` the highest number, an active and an archived provisional ticket (the second depending on the first), and `TASK-3` itself listing one in `depends_on` and mentioning both in its Description: the provisional tickets get `TASK-4` and `TASK-5` in ascending order of their provisional suffixes; both files are moved in their own directories, lose `provisional`, and have `moved_from` set to their provisional IDs; the second's `depends_on` names the first's new ID; `TASK-3`'s `depends_on` and Description are rewritten and its History is not; one commit names all three in `Task:` trailers; a variant with `TASK-3` archived (so the highest number is only in the archive) still gives `TASK-4` and `TASK-5`; and a variant creating them in reverse order (`side_effect=[1] + [0] * 5 + [0] * 6`, so `TASK-BAAAAA` is made first) gives the same result, because the order comes from the IDs, not from file listing
- [ ] A second call returns no changes and makes no commit; off `main` and on a detached `HEAD` it raises `ChittyError` and changes nothing
- [ ] With a `.git/hooks/pre-commit` that exits 1, the call raises `ChittyError` containing `autocommit failed`, and `git status --porcelain` and every ticket file's bytes equal what they were before; with a ticket file planted in `chitty/tasks/` under a valid name but unparseable content, it raises `ChittyError` naming that file, and every ticket file's bytes and `git status --porcelain` equal their values before the call; with two files sharing one provisional ID, it raises naming both paths, and every ticket file's bytes and `git status --porcelain` equal their values before the call
- [ ] Outside a Git repository (a temporary directory with `chitty.toml` and `autocommit = false`, and a file `chitty/tasks/TASK-AAAAAA--x.md` with `provisional: true`), the call renumbers it to `TASK-1` without error, and no `.git` directory is created. On `main`, with `TASK-3` depending on both a dangling `TASK-4` (no such file) and the provisional `TASK-AAAAAA`, the provisional ticket becomes `TASK-5`, and `TASK-3`'s `depends_on` becomes `[TASK-4, TASK-5]`. `make check` passes
- [ ] `TASK-3`, the highest-numbered ticket, is in flight on branch `task-3` (one commit ahead of `main`) while its `main` copy mentions a provisional ID: its `main` file is left byte-identical, the two provisional tickets on `main` still become `TASK-4` and `TASK-5` (the skipped ticket's number counts as used), and the commit's `Task:` trailers name those tickets and not `TASK-3`

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
