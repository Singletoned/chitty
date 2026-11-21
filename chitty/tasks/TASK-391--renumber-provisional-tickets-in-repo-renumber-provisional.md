---
title: Renumber provisional tickets in `Repo.renumber_provisional`
status: planning
depends_on:
  - TASK-381
  - TASK-389
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` and `provisional: true` (`TASK-380`, `TASK-389`). Once it reaches `main` it should get an ordinary sequential number. This is cosmetic and idempotent. This ticket builds the store method; `TASK-392` wires it to the CLI.

Starts after `TASK-381` (`plan_renumbering`, `replace_ids`) and `TASK-389` land.

Decisions:

- New `Repo.renumber_provisional() -> tuple[Change, ...]` in `src/chitty/store.py`, returning one `Change` per renumbered ticket (empty when none).
- It acts only "on `main`": outside a Git repository (`git.is_repository` false), or in one whose current branch is the main branch. Off `main`, including a detached `HEAD`, it raises `ProvisionalOffMain`, a new `ChittyError` subclass in `src/chitty/errors.py`, saying provisional tickets are renumbered on main; the CLI turns that into a no-op (`TASK-392`).
- It works on this checkout's ticket files on disk (active and archive directories of every context), but skips every file whose ticket `Repo` reads from another ref (`StoredTask.branch` is not `None`, after `TASK-378`): the main checkout also holds `main`'s stale copies of in-flight tickets, and writing them would make the ticket change on both sides. Such tickets, and tickets only on other branches, keep their mentions of the old ID (dangling; accepted).
- First parse every ticket file and plan everything (`plan_renumbering`), so an unparseable file fails before any write. Two files with the same provisional ID make `plan_renumbering` raise; `renumber_provisional` adds both paths to the message and writes nothing (`chitty renumber PATH` then separates them).
- Extract `Repo._used_numbers(context) -> set[int]` from `next_number`, keeping everything `next_number` counts (active and archive files, and `_deleted_numbers` in delete mode); `next_number` then returns `ids.next_number` of it for sequential contexts, its random branch unchanged. Pass those sets to `plan_renumbering`. A provisional ticket in a `random_ids` context is left alone.
- For each renumbered ticket: a new helper (do not change `_relocate`, which `move` and `renumber PATH` share) moves the file to the new ID with the same slug in the same directory (active or archive), removes `provisional`, sets `moved_from` to the provisional ID (replacing any earlier value), and adds a History event `renumbered from <old ID>`.
- Rewrite mentions in every ticket file on disk through a new pure function `rewrite_task(task: Task, mapping: Mapping[TaskId, TaskId]) -> Task` in `src/chitty/renumbering.py`: `replace_ids` on `title`, `depends_on`, `parent`, the text before the first section, and every section except `History`, which is append-only; Acceptance Criteria per item in two calls, because a `set_criteria` item comes back unchecked and `with_section` refuses that section: `with_criteria(add=(), remove=(), set_criteria=<changed items>, check=(), uncheck=())`, then `with_criteria(add=(), remove=(), set_criteria=(), check=<indices checked before>, uncheck=())`. (`TASK-380` adds `provisional` to `FIELD_ORDER`, so `with_field("provisional", None)` works.) `moved_from` is not rewritten, so a renumbered file's own `moved_from` and History keep the provisional ID.
- Order: `_prepare_write()` first; snapshot ticket files with `_task_file_bytes` and the index bytes; compute every affected file's final `Task` and path in memory (a renamed ticket's rewrites applied to its renamed content); write each file once at its final path with `_write` (not `_save`, which applies the current-version guard and dependency checks) and remove old paths; then one `_commit(change, "renumber provisional tickets")` whose `Task:` trailers name every renamed and rewritten ticket, as `archive_done` batches. On any exception after the snapshot (including `chitty fix` validation, formatting, or `autocommit failed` from `git.commit`), restore the ticket files with `_restore_task_files` and the index bytes, call `self._invalidate()`, then re-raise. Outside a Git repository no commit is made. Do not copy `Repo.edit`'s test for a particular message.

Tests: real-file tests calling `Repo.renumber_provisional()` in a new `tests/test_renumber_provisional.py`, inheriting `RepoTestCase` from `tests/support.py`, running `git init -b main`, setting `user.name` and `user.email` as `tests/test_autocommit.py` does, and `autocommit = true` (its default config has `autocommit = false`). A Hypothesis property for `rewrite_task` in `tests/test_property_renumbering.py` (`TASK-381`'s file): for generated tickets mentioning old IDs in every field and section, every non-History mention is rewritten, the rendered `History` section is byte-identical, criteria keep their checked state, and with an identity mapping the rendered output equals the input. Text includes near misses (`TASK-K7Q2MXA`, `XTASK-K7Q2MX`), which stay unchanged, and mentions inside code spans and URLs, which are rewritten (they match `TASK-381`'s rule). Patch the provisional draw (`_provisional_draw`, `TASK-389`) in the real-file tests so suffixes, and so the order that gives `TASK-4` and `TASK-5`, are known. Make provisional tickets with `chitty add` on a branch (archive one there), `git switch main`, `git merge` the branch, and stay on `main`. No property beyond `TASK-381`'s: file plumbing over the cases in the criteria.

## Acceptance Criteria

- [ ] On `main`, with `TASK-3` the highest number, an active and an archived provisional ticket (the second depending on the first), and `TASK-3` itself listing one in `depends_on` and mentioning both in its Description: the provisional tickets get `TASK-4` and `TASK-5` in ascending order of their provisional suffixes; both files are moved in their own directories, lose `provisional`, and have `moved_from` set to their provisional IDs; the second's `depends_on` names the first's new ID; `TASK-3`'s `depends_on` and Description are rewritten and its History is not; one commit names all three in `Task:` trailers
- [ ] A second call returns no changes and makes no commit; off `main` and on a detached `HEAD` it raises `ChittyError` and changes nothing; a ticket existing only on another branch that mentions a provisional ID is left unchanged there and does not stop the run
- [ ] With a `.git/hooks/pre-commit` that exits 1, the call raises `ChittyError` containing `autocommit failed`, and `git status --porcelain` and every ticket file's bytes equal what they were before; with a ticket file planted in `chitty/tasks/` under a valid name but unparseable content, it raises `ChittyError` naming that file before writing anything; with two files sharing one provisional ID, it raises naming both paths and writes nothing
- [ ] The `rewrite_task` property passes and fails against a `NotImplementedError` stub; `make check` passes
- [ ] A ticket in flight on `task-<n>` whose `main` copy mentions a provisional ID is left byte-identical on `main`, and the rest of the run succeeds

## Notes

The requested rewrite and property cannot be implemented as written against the current model: `src/chitty/model.py` `_split_sections` rejects any non-whitespace content before the first `##` section, so a parsed `Task` cannot contain an ID in the preamble. The description nevertheless requires rewriting that text and generating tickets with mentions in every field and section; frontmatter fields such as `status`, `created` and `provisional` also cannot contain such mentions, while `moved_from` and History are explicitly excluded from rewriting. Please specify whether to change the parser to allow preamble content or remove that requirement, and clarify the property fixture to identify the eligible fields and sections. No implementation was started; regression evidence and verification remain outstanding.

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
