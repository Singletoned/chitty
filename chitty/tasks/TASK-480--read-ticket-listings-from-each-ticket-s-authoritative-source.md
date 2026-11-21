---
title: Read ticket listings from each ticket's authoritative source, not every ref's history
status: todo
depends_on:
  - TASK-378
  - TASK-515
  - TASK-518
parent: TASK-376
created: 2026-11-20
---

## Description

Use authoritative ticket sources for listings. `TASK-378` landed source selection and `TASK-515` landed shared Git metadata. Keep changes in `src/chitty/store.py`. Land after `TASK-518` so `show` is no longer coupled to strict listings. Keep behavior of actual reference rewrites unchanged; the only move adjustment allowed here is skipping saves for tickets with no matching reference.

Replace the history merge in `_tasks_in_location` with `ticket_ids()` and the same source resolver and parser as `lookup`. Resolve source before deciding active/archive and context, and use the selected file's directory, not the prefix or a stale working-tree path. Keep existing sorting, context discovery and `_invalidate` semantics. Use `_source_files` to resolve, skip empty results, and parse only when a selected path belongs to the requested location; call `_parse_source_copy` with the full match set so duplicate IDs spanning locations are not masked. Source selection errors propagate: it takes selection to know the authoritative location. A malformed body at an unselected or superseded location must not itself fail a listing. `all_tasks()` continues to use configured contexts; default CLI `list` also includes discovered contexts. Remove the now-unused Repo history/dirty-path listing helpers and associated caches; do not remove the Git APIs themselves here.

`new_id` on a sequential context off main must take used provisional IDs from `ticket_ids()`, not `all_tasks()`, so creation does not depend on other bodies. In `move`, skip `_save` for each unrelated ticket when neither `depends_on` nor `parent` names the old ID: there is nothing to write, and `_save` checks write authority before its no-change check. Keep `_save` and its authority check for actual rewrites. This keeps `tests/test_provisional_ids.py::test_move_provisional_off_main_then_promote_on_main` passing on the authoritative listings. No change to single-ticket `archive` or the existing bulk `archive` algorithm; bulk archive needs the active tickets and therefore propagates their conflicts.

Tests: new `tests/test_authoritative_listing.py`, real files and real Git, use `CliTestCase` and the Git fixture helpers used in `tests/test_source_copy_errors.py`. Fixed Git integration states exercise the wiring; the pure rules are already generated in `tests/test_property_ticket_source.py`. Confirm the changed listing and isolated allocation assertions fail before the fix, then run the new suite and `make check`. Use a test-local `git.historical_files` patch only in the placement/standalone cases; the conflict test must distinguish conflict detection from an arbitrary failure.

Placement: commit an active `TASK-1` and active `TASK-2` on main. On `task-1`, move its file into `archive/`, change its title, and commit. On `task-2`, change its title and commit, then return to main and corrupt only the stale working-tree `TASK-2` body. Assert `lookup` selects those branches. `tasks(active)` and CLI list show the branch title for `TASK-2`, plus the branch-only `TASK-3` described below; `tasks(archived)` has only the branch title for `TASK-1`; `all_tasks` includes every fixture ticket exactly once. Assert the branch-only ticket also resolves with `lookup`. Run the Git placement assertions once unpatched as well so a regression cannot fail merely because the legacy history API is patched. Also make a valid branch-only `TASK-3` on `task-3` and expect it in active results (still absent from disk on main). For the no-Git case create a valid active ticket on disk and list it with `git.historical_files` patched to raise. Preserve context behavior using the existing CLI suite.

Conflict: use the changed-on-both fixture pattern from `tests/test_source_copy_errors.py` (`TASK-1` changed separately on main and `task-1`), with `autocommit = false` and current setup. On main assert `list --json` and `archive` without an ID fail with `TASK-1` and `changed on both`. Snapshot ticket files, HEAD and index around bulk archive and assert no changes. On a separate branch from main, also plant a different malformed active ticket under a valid ticket filename (so the old allocator that parses every ticket fails); patch the draw to produce an existing committed `TASK-AAAAAA` first and `TASK-BAAAAA` next; `add` succeeds with `TASK-BAAAAA` and the existing file is unchanged. Use `mock.patch` on `chitty.store._provisional_draw` as in the provisional allocation tests.

## Acceptance Criteria

- [ ] The real-Git placement fixture separately asserts `lookup`, `Repo.tasks` for active and archived, `all_tasks`, and default `chitty list --json` agree with the specified results for all three tickets, including the branch-only and moved tickets. Repeat with `git.historical_files` patched to raise; standalone listing under the patch returns the on-disk ticket.
- [ ] With a ticket changed on both its own branch and main, `chitty list --json` and bulk `archive` fail with `TASK-1` and `changed on both`; bulk archive leaves files, HEAD and index unchanged. Off-main `add` from the conflict fixture also tolerates another ticket with a malformed body, retries the occupied provisional ID and returns the next one.
- [ ] Keep `tests/test_list_performance.py` passing, including constant Git count with no ticket branches and cache invalidation, and keep `test_move_provisional_off_main_then_promote_on_main` passing without relaxing write authority for actual rewrites. Show the move regression by running that test on the cutover with only the no-op skip removed. `make check` passes after the prerequisite lands.
- [ ] In a standalone repo put valid `TASK-1` copies in both active and archive directories. Default listing fails with the duplicate-ID error and both paths, rather than hiding the archived duplicate.

## Plan

Replace location history merging with authoritative source selection, switch provisional allocation to ticket IDs, and cover placement, conflicts, duplicate IDs, and standalone listing with real Git regression tests. Run the new tests before and after the change, then format and check.

## Notes

Placeholder from the 2026-11-20 split of `TASK-378`; plan it after `TASK-378` lands. Scope: switch `_tasks_in_location` (so `tasks`, `all_tasks` and `chitty list`) to `ticket_ids()` plus `source_copy`, and apply the rule decided with the owner on 2026-11-20: an operation fails only if it needs the conflicted ticket's content. Isolated: `add` (free IDs only; `new_id` on a ticket branch uses `ticket_ids()`), `move <ID>` and `archive <ID>` (fail only when `<ID>` is the conflicted ticket). Fail naming the conflicted ticket: `list`, `archive` with no ID, and `renumber`. Also take over the former `TASK-378` criterion 4: with `git.historical_files` patched to raise, `chitty list` and `chitty show` still work, and outside Git `chitty list` reads the working tree.

Open decision for this ticket: `chitty show` lists a ticket's children through `all_tasks()` (`src/chitty/cli.py`, `show`), which needs every ticket's `parent`, which is content. After the switch, one conflicted ticket would make `show` of any ticket fail. Decide whether `show` skips the conflicted ticket when listing children, with a warning naming it, or fails.

Also: `_collect_ticket_ids` reads the content of every ticket file on `main` and on each ticket branch (`git.files_at`); check `tests/test_list_performance.py` against that.

Regression tests to include, from superseded `TASK-367`: with `autocommit = true`, add `TASK-1`, add `TASK-2 --parent TASK-1`, set `TASK-1` done, then `chitty archive TASK-1` succeeds, commits and leaves `git status` clean; and in a worktree made before `main` archived `TASK-2`, `chitty edit TASK-1 --depends-on TASK-2` succeeds and `chitty show TASK-2 --json` reports it archived.

Planner, 2026-11-21: the two regression tests from `TASK-367` listed above now live on `TASK-367` itself (depends on `TASK-378`); do not add them here.

Found 2026-11-21 by `TASK-506`'s worker: after `TASK-378`, `chitty show TASK-1` still fails when another working-tree ticket file is malformed. In the fixture, `TASK-1` is committed valid on `main` and edited (title `branch`) on `task-1`, then the main checkout's `TASK-1` file is overwritten, uncommitted, with `not frontmatter`. `show` lists the ticket's children through `repo.all_tasks()` (`src/chitty/cli.py:604`), which parses every working-tree copy. Once listings read from each ticket's source, `chitty show TASK-1` there should print title `branch`. Make that a criterion of this ticket.

Split out the source-lookup performance prerequisite before switching listings. A real-Git probe on `main` did `Repo.lookup` for every ID from `Repo.ticket_ids()` and counted 16 Git invocations for two tickets and 56 for ten, even with no ticket branches. The existing constant-count check in `tests/test_list_performance.py` must still pass after listings switch.

Keep the listing cutover separate from write-path repair. Before the cutover, audit write callers of `all_tasks()` against the existing rule that a conflict fails only operations needing its content: `move` actually reads other tickets to rewrite references, and single-ticket `archive` in delete mode does too. Do not promise conflict isolation for those paths until reference discovery can provide it. For `show --json`, do not scan for children (they are not in the JSON response). For plain `show`, keep the child list and warn about unreadable candidates rather than hiding the selected readable ticket; a failure to read the selected ticket itself still fails the command. Specify those as separately verifiable changes if necessary.

Planning blocker: the specified cutover conflicts with the requirement that `make check` pass while child discovery in `show` is explicitly out of scope. After the cutover, `make check` fails in `tests.test_promote_references_cli.TestPromoteReferencesCli.test_duplicate_reference_is_reported_without_failing_promotion`, two `tests.test_reference_isolation` tests, and `tests.test_ticket_reads.TestTicketReads.test_conflict_does_not_prevent_other_reads_or_edit`: `show` calls `all_tasks()` and now fails on an unrelated duplicate or conflict. TASK-518 covers this but is still in planning, not a dependency. Decide whether to land TASK-518 first and add it as a dependency, or include its changes here.

A fifth failure is `tests.test_provisional_ids.TestProvisionalIds.test_move_provisional_off_main_then_promote_on_main`: the cutover makes `move` fail because a reference rewrite attempts to write TASK-1 on main from another branch. The ticket excludes move changes yet requires the full suite to pass. Decide the intended move behavior and whether its repair is a prerequisite or in scope; do not weaken the existing assertion without that decision.

Partial implementation and two tests are committed. Before the fix both new tests failed: placement parsed the corrupted stale TASK-2, and standalone listing invoked patched `historical_files`; both pass after it. Remaining specified conflict, allocation, duplicate and CLI coverage is not yet implemented, so full acceptance could not be verified. `make check` passes formatting, Ruff and Pyright but fails the five tests above.

Planning blocker: the authoritative listing cutover breaks existing show and move tests, while both repairs are out of scope and make check must pass. See the preceding note for failures and decisions needed.

## History

- 2026-11-20T22:59:14Z quick-pearl-lapwing → backlog
- 2026-11-20T22:59:58Z quick-pearl-lapwing: changed notes
- 2026-11-20T23:21:39Z quick-pearl-lapwing: changed notes
- 2026-11-21T08:05:17Z nimble-umber-gannet: changed notes
- 2026-11-21T12:43:40Z sunny-ebony-kestrel: changed notes
- 2026-11-21T15:51:34Z honest-coral-heron: changed notes
- 2026-11-21T15:51:34Z honest-coral-heron backlog → planning
- 2026-11-21T15:51:58Z honest-coral-heron: changed dependencies
- 2026-11-21T18:38:35Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:38:35Z eager-ginger-adder planning → cold-read
- 2026-11-21T18:39:43Z eager-ginger-adder cold-read → planning
- 2026-11-21T18:40:09Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:40:09Z eager-ginger-adder planning → cold-read
- 2026-11-21T18:42:26Z eager-ginger-adder cold-read → planning
- 2026-11-21T18:42:29Z eager-ginger-adder planning → todo
- 2026-11-21T18:43:08Z calm-pearl-yellowhammer todo → doing
- 2026-11-21T18:44:33Z calm-pearl-yellowhammer: wrote the plan
- 2026-11-21T18:47:35Z calm-pearl-yellowhammer: changed notes
- 2026-11-21T18:47:42Z calm-pearl-yellowhammer: changed owner, notes
- 2026-11-21T18:47:42Z calm-pearl-yellowhammer doing → planning
- 2026-11-21T18:50:23Z eager-ginger-adder: changed dependencies, description, acceptance criteria
- 2026-11-21T18:50:23Z eager-ginger-adder planning → cold-read
- 2026-11-21T18:53:00Z eager-ginger-adder cold-read → planning
- 2026-11-21T18:53:03Z eager-ginger-adder planning → todo
