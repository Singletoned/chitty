---
title: Read ticket listings from each ticket's authoritative source, not every ref's history
status: planning
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-20
---

## Description

This ticket needs refining.

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
