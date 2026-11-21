---
title: Plan provisional renumbering without writing
status: cold-read
depends_on:
  - TASK-381
  - TASK-389
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

Prepare read-only inputs to the store transaction in `TASK-517`. Do not add a command or write files. Relevant code: `src/chitty/store.py`, `src/chitty/renumbering.py`, `src/chitty/errors.py`.

- Add `Repo._plan_provisional_renumbering() -> tuple[dict[TaskId, TaskId], tuple[StoredTask, ...]]`: the old-to-new ID mapping and writable disk tickets, including unchanged IDs. Use fresh `git.is_repository` and `git.current_branch` before discovery; in Git require the configured `Repo._main_branch()` (not detached HEAD). Otherwise raise new `ProvisionalOffMain(ChittyError)` saying provisional tickets are renumbered on main. Outside Git proceed. Never call `_prepare_write`.
- Scan and parse active and archived disk files in all `discovered_contexts()`; errors name the path. Only configured files with `source_of(id)` equal to `None` are writable. A writable file with `provisional: true` in a sequential context is a candidate; random contexts may be rewritten, not renumbered. Reject any duplicate on-disk ID involving a candidate before invoking `plan_renumbering`, naming both paths. Return `({}, ())` if there are no candidates after discovery.
- Extract `_used_numbers(context) -> set[int]` without changing `next_number` behavior (active/archive plus `_deleted_numbers` in delete mode). For each sequential prefix reserve those numbers, integer IDs from `ticket_ids()` (including unconfigured, skipped and branch-only filenames), and integer references from `ids.ticket_references` over the scanned disk files. Pass the sets and candidates to `plan_renumbering`; it owns order and allocation. Let source-selection errors propagate.
- If there is a plan, reject a `parent` or `depends_on` pointing to any old ID in an untouched disk file or visible authoritative ref-backed ticket. Use `ticket_ids()` and `lookup` for ref-backed results, including IDs without a disk file. A read error for a source needed by preflight propagates. Compare structured links via `TaskId.parse`; name the blocking ticket and old ID. Ignore prose and History in this guard, and do not inspect non-authoritative historical refs or unseen branches.

Tests in `tests/test_provisional_preflight.py`: `RepoTestCase`, valid rendered provisional files written directly for deterministic IDs, real Git with `git init -b main`, local author and committed fixture. Fixed integration states: the pure allocator already has generated ordering/allocation tests (`TASK-381`). Demonstrate behavioral failures on a signature stub raising `NotImplementedError`, then pass the new tests and `make check`.

Allocation: archive `TASK-AAAAAA`, leave `TASK-BAAAAA` active, with highest number `TASK-3`; reverse creation order and expect `TASK-4` and `TASK-5` in both orders. With the same base, separately make the sole higher number `TASK-4` archived, unconfigured, read from its own ticket branch, present only on its ticket branch, mentioned in a Description, or deleted after committing in delete mode. Each variant must yield `TASK-5` and `TASK-6`. Assert reference selection in branch fixtures; assert both candidates and a flag-bearing provisional file in a separate configured random context are writable but only the sequential candidates are mapped. Add an unconfigured provisional file and assert it is neither mapped nor writable. An empty fixture returns an empty plan. Use a slug-matching malformed file and two distinct paths for the same provisional ID for the error tests; stale setup means removing and committing `chitty_version`.

Untouched-source fixtures: separately link to `TASK-AAAAAA` from (a) an unconfigured disk file, (b) a stale main file whose authoritative ticket branch removes the link, and (c) an authoritative branch-only ticket. Use `depends_on` for (a) and (c), lowercase `parent` for (b), and assert the selected refs for (b) and (c). In the prose variants put the old ID in Description instead of the structured link.

## Acceptance Criteria

- [ ] The real-file allocation fixtures return the exact mapping and writable paths without changing HEAD, index or file bytes; a fixture outside Git maps the sole `TASK-AAAAAA` to `TASK-1`.
- [ ] With stale setup, an off-main branch and detached HEAD each raise `ProvisionalOffMain`; on main, an unparseable file or duplicate candidate raises `ChittyError` naming the bad path or both duplicate paths respectively. In each case compare HEAD, index and file bytes before and after.
- [ ] Each untouched-source structural link fixture refuses the batch, names both IDs and leaves HEAD, index and file bytes unchanged; replacing that link with a Description mention allows the plan and keeps the same files excluded from the writable set.

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

Two issues need decisions before the specified allocation and finalization can be implemented:

1. Unconfigured directories are excluded from allocation, but `check.fix` checks duplicate IDs across `discovered_contexts()`, including unconfigured directories. For example, an unconfigured `chitty/other/TASK-1--x.md` and a configured provisional `TASK-AAAAAA` with no used configured numbers make the specified allocator choose `TASK-1`; finalization then rejects the duplicate and rolls back. The ticket requires unconfigured files to remain unchanged but does not decide whether their numeric IDs must be reserved, a collision should be rejected, or this case is otherwise handled. Please specify the desired behavior and a real-file fixture, action and assertions, including unchanged unconfigured bytes and commit or rollback as appropriate.
2. The description asks to union used numbers where configured contexts share a prefix, but `RepoConfig._consistent` in `src/chitty/config.py` rejects duplicate context prefixes. Please reconcile that requirement with the configuration model and specify whether shared prefixes should be supported or the unreachable instruction removed; supporting them also needs allocation tests.

No implementation or tests were written. Regression evidence and verification remain outstanding.

Planner 2026-11-21: filenames in unconfigured directories reserve their numbers (case added to criterion 2); removed the unreachable shared-prefix union.

The required ordering conflicts with the no-change and preflight guarantees for a stale setup. `Repo._prepare_write()` can run `init_repo` and make a `chitty: upgrade repository setup` commit before returning when autocommit is enabled in a non-linked Git checkout; `tests/test_init_workflow.py::test_autocommit_upgrade_precedes_add` documents that behavior. Because the ticket requires calling it first, an off-main call can modify and commit setup before raising, contrary to criterion 2, and a call with an unparseable file can modify and commit setup before parsing, contrary to the requirement to fail before any write. The setup upgrade is outside `_all_or_nothing`, so rollback does not undo it either. Please decide whether setup upgrades are an explicit exception to these guarantees or whether branch/preflight checks must precede setup preparation, and specify real-file stale-setup fixtures, actions and assertions for off-main and parse-failure cases. No implementation or tests were written; regression evidence and verification remain outstanding.

Planner 2026-11-21: the main-branch check and parse-and-plan now run before `_prepare_write()`, so off-`main` calls and parse failures never upgrade setup (stale-setup case added to criterion 2). A setup upgrade on a real write is outside the rollback, as for every write.

This ticket is too large to implement and verify confidently in one session: its five criteria combine the new allocation and rewrite operation with more than a dozen distinct real-Git scenarios, including archive/delete allocation, source-ref selection, unconfigured and random contexts, stale setup, standalone operation, and transactional rollback. Please split it into smaller dependent tickets with independently verifiable fixtures and assertions, deciding which slice owns the initial store method and how later slices extend it. I inspected the ticket, `src/chitty/store.py`, `src/chitty/renumbering.py`, `src/chitty/ids.py`, and `src/chitty/check.py`; no implementation or tests were written, so regression evidence and verification remain outstanding.

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
- 2026-11-21T14:46:43Z jolly-quartz-wren todo → doing
- 2026-11-21T14:49:10Z jolly-quartz-wren: changed owner, notes
- 2026-11-21T14:49:10Z jolly-quartz-wren doing → planning
- 2026-11-21T14:49:49Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T14:49:49Z sunny-ebony-kestrel planning → todo
- 2026-11-21T14:50:20Z youthful-yellow-newt todo → doing
- 2026-11-21T15:12:45Z youthful-yellow-newt: changed owner, notes
- 2026-11-21T15:12:45Z youthful-yellow-newt doing → planning
- 2026-11-21T15:14:23Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T15:14:23Z sunny-ebony-kestrel planning → todo
- 2026-11-21T15:19:37Z youthful-dusky-raven todo → doing
- 2026-11-21T15:23:00Z youthful-dusky-raven: changed owner, notes
- 2026-11-21T15:23:00Z youthful-dusky-raven doing → planning
- 2026-11-21T18:34:34Z eager-ginger-adder: changed title, dependencies, description, acceptance criteria; wrote the plan
- 2026-11-21T18:34:34Z eager-ginger-adder planning → cold-read
