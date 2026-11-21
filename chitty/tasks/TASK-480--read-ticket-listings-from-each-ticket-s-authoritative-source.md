---
title: Read ticket listings from each ticket's authoritative source, not every ref's history
status: planning
depends_on:
  - TASK-378
  - TASK-515
parent: TASK-376
created: 2026-11-20
---

## Description

Use authoritative ticket sources for listings. `TASK-378` landed source selection and `TASK-515` landed shared Git metadata. Keep changes in `src/chitty/store.py`. Child discovery in `show` is separate (`TASK-518`); changing write paths that really need other ticket bodies (e.g. `move` reference rewrites or `archive ID` in delete mode) is out of scope.

Replace the history merge in `_tasks_in_location` with `ticket_ids()` and the same source resolver and parser as `lookup`. Resolve source before deciding active/archive and context, and use the selected file's directory, not the prefix or a stale working-tree path. Keep existing sorting, context discovery and `_invalidate` semantics. Use `_source_files` to resolve, skip empty results, and parse only when a selected path belongs to the requested location; call `_parse_source_copy` with the full match set so duplicate IDs spanning locations are not masked. Source selection errors propagate: it takes selection to know the authoritative location. A malformed body at an unselected or superseded location must not itself fail a listing. `all_tasks()` continues to use configured contexts; default CLI `list` also includes discovered contexts. Remove the now-unused Repo history/dirty-path listing helpers and associated caches; do not remove the Git APIs themselves here.

`new_id` on a sequential context off main must take used provisional IDs from `ticket_ids()`, not `all_tasks()`, so creation does not depend on other bodies. No change to `move`, single-ticket `archive`, or the existing bulk `archive` algorithm; bulk archive needs the active tickets and therefore propagates their conflicts.

Tests: new `tests/test_authoritative_listing.py`, real files and real Git, use `CliTestCase` and the Git fixture helpers used in `tests/test_source_copy_errors.py`. Fixed Git integration states exercise the wiring; the pure rules are already generated in `tests/test_property_ticket_source.py`. Confirm the changed listing and isolated allocation assertions fail before the fix, then run the new suite and `make check`. Use a test-local `git.historical_files` patch only in the placement/standalone cases; the conflict test must distinguish conflict detection from an arbitrary failure.

Placement: commit an active `TASK-1` and active `TASK-2` on main. On `task-1`, move its file into `archive/`, change its title, and commit. On `task-2`, change its title and commit, then return to main and corrupt only the stale working-tree `TASK-2` body. Assert `lookup` selects those branches. `tasks(active)` and CLI list have only the branch title for `TASK-2`; `tasks(archived)` has only the branch title for `TASK-1`; `all_tasks` includes both exactly once. Also make a valid branch-only `TASK-3` on `task-3` and expect it in active results (still absent from disk on main). For the no-Git case create a valid active ticket on disk and list it with `git.historical_files` patched to raise. Preserve context behavior using the existing CLI suite.

Conflict: use the changed-on-both fixture pattern from `tests/test_source_copy_errors.py` (`TASK-1` changed separately on main and `task-1`), with `autocommit = false` and current setup. On main assert `list --json` and `archive` without an ID fail with `TASK-1` and `changed on both`. On a separate branch from main, patch the draw to produce an existing committed `TASK-AAAAAA` first and `TASK-BAAAAA` next; `add` succeeds with `TASK-BAAAAA` and the existing file is unchanged. Use `mock.patch` on `chitty.store._provisional_draw` as in the provisional allocation tests.

## Acceptance Criteria

- [ ] In the real-Git placement fixture, `Repo.tasks` and `all_tasks` agree with authoritative `lookup` on each selected ticket and list it once in its authoritative location; `chitty list --json` shows only the active authoritative results. Patch `git.historical_files` to raise throughout, and cover standalone working-tree listing the same way.
- [ ] In the real-Git conflict fixture `chitty list --json` and bulk `archive` fail naming `TASK-1` without reading a non-authoritative copy; off-main `add` succeeds with an unused provisional ID despite that conflict.
- [ ] Keep `tests/test_list_performance.py` passing, including constant Git invocation count with no ticket branches and invalidation after an edit on the same `Repo`; `make check` passes.

## Notes

Placeholder from the 2026-11-20 split of `TASK-378`; plan it after `TASK-378` lands. Scope: switch `_tasks_in_location` (so `tasks`, `all_tasks` and `chitty list`) to `ticket_ids()` plus `source_copy`, and apply the rule decided with the owner on 2026-11-20: an operation fails only if it needs the conflicted ticket's content. Isolated: `add` (free IDs only; `new_id` on a ticket branch uses `ticket_ids()`), `move <ID>` and `archive <ID>` (fail only when `<ID>` is the conflicted ticket). Fail naming the conflicted ticket: `list`, `archive` with no ID, and `renumber`. Also take over the former `TASK-378` criterion 4: with `git.historical_files` patched to raise, `chitty list` and `chitty show` still work, and outside Git `chitty list` reads the working tree.

Open decision for this ticket: `chitty show` lists a ticket's children through `all_tasks()` (`src/chitty/cli.py`, `show`), which needs every ticket's `parent`, which is content. After the switch, one conflicted ticket would make `show` of any ticket fail. Decide whether `show` skips the conflicted ticket when listing children, with a warning naming it, or fails.

Also: `_collect_ticket_ids` reads the content of every ticket file on `main` and on each ticket branch (`git.files_at`); check `tests/test_list_performance.py` against that.

Regression tests to include, from superseded `TASK-367`: with `autocommit = true`, add `TASK-1`, add `TASK-2 --parent TASK-1`, set `TASK-1` done, then `chitty archive TASK-1` succeeds, commits and leaves `git status` clean; and in a worktree made before `main` archived `TASK-2`, `chitty edit TASK-1 --depends-on TASK-2` succeeds and `chitty show TASK-2 --json` reports it archived.

Planner, 2026-11-21: the two regression tests from `TASK-367` listed above now live on `TASK-367` itself (depends on `TASK-378`); do not add them here.

Found 2026-11-21 by `TASK-506`'s worker: after `TASK-378`, `chitty show TASK-1` still fails when another working-tree ticket file is malformed. In the fixture, `TASK-1` is committed valid on `main` and edited (title `branch`) on `task-1`, then the main checkout's `TASK-1` file is overwritten, uncommitted, with `not frontmatter`. `show` lists the ticket's children through `repo.all_tasks()` (`src/chitty/cli.py:604`), which parses every working-tree copy. Once listings read from each ticket's source, `chitty show TASK-1` there should print title `branch`. Make that a criterion of this ticket.

Split out the source-lookup performance prerequisite before switching listings. A real-Git probe on `main` did `Repo.lookup` for every ID from `Repo.ticket_ids()` and counted 16 Git invocations for two tickets and 56 for ten, even with no ticket branches. The existing constant-count check in `tests/test_list_performance.py` must still pass after listings switch.

Keep the listing cutover separate from write-path repair. Before the cutover, audit write callers of `all_tasks()` against the existing rule that a conflict fails only operations needing its content: `move` actually reads other tickets to rewrite references, and single-ticket `archive` in delete mode does too. Do not promise conflict isolation for those paths until reference discovery can provide it. For `show --json`, do not scan for children (they are not in the JSON response). For plain `show`, keep the child list and warn about unreadable candidates rather than hiding the selected readable ticket; a failure to read the selected ticket itself still fails the command. Specify those as separately verifiable changes if necessary.

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
