---
title: Show the 🔗 dependency glyph in `chitty list` for every unfinished ticket
status: doing
parent: TASK-70
created: 2026-11-19
---

## Description

Seen 2026-11-19: `TASK-450` is in `planning` with `depends_on: TASK-426, TASK-430`, but `chitty list` shows nothing in its marker column, so a planner cannot see that it waits on another ticket. The column shows `skip_reason` (`src/chitty/selection.py`): why `chitty next`/`chitty run` would skip a ticket. That returns `None` for any status outside `review`, `doing` and `todo` (its first check, before the lock, human and owner checks, so it is `None` for every `planning` or `cold-read` ticket), and `_selection_facts` (`src/chitty/store.py`) reads dependencies only for `todo`. A slice of `TASK-70` criterion 1.

Decisions:

- The dependency glyph changes from 🔒 to 🔗 (owner, 2026-11-19, recorded on `TASK-70`: one code point, always two columns wide). Add the module constant `DEPENDENCY_GLYPH = "🔗"` in `src/chitty/selection.py` and use it in `skip_reason`'s `waits on` text.
- `skip_reason` and `choose` keep their meaning: they are about selection. `chitty next`, `chitty run` and `chitty list --json` (`skipped`) do not change, apart from the glyph.
- The marker states a fact about the ticket, not about which statuses the runner picks today (owner, 2026-11-19: `work` and `review` are not the only modes there will be; there may be separate `code` and `graphics` agents, a `write-tests` step before `work`, or several kinds of review). So the new rule names no status other than `done`. New pure function in `src/chitty/selection.py`: `dependency_marker(fact: TicketFacts) -> str | None`. It returns `None` when the ticket is archived or `done`. Then, checking `fact.dependencies` in order: the first `broken` one gives exactly the text `skip_reason` gives for a broken dependency (`⚠️ <ID> depends on <reference>: <error>`); otherwise any `unfinished` ones give `🔗 waits on <references joined by ", ">`; otherwise `None`.
- `_selection_facts` reads dependencies when `dependencies` is true and the ticket is not archived (today only for `todo`).
- New `list_marker(repo: Repo, stored: StoredTask) -> str | None` in `src/chitty/store.py`: `skip_reason(repo, stored)` if that is not `None` (so running, human and owner markers, and a `todo` ticket's own dependency reason, keep precedence); otherwise `dependency_marker` of `_selection_facts(repo, stored, locked=<as skip_reason reads it>, dependencies=True)`. The text output of `chitty list` (`src/chitty/cli.py`) uses `list_marker` instead of `skip_reason` for its marker column and its broken-dependency `warning:` line; its `--json` branch keeps `skip_reason`.
- Docs: replace 🔒 with 🔗 in `README.md` (line 96), `docs/plan/cli.md` (lines 46 and 50) and `docs/plan/next-action-and-runner.md` (line 16); in `docs/plan/cli.md`, say that every unfinished ticket that is not running, not human and has no owner shows 🔗 or ⚠️ for its dependencies, whatever its status; the running, human and owner markers come first.
- Out of scope: which statuses `chitty next` and `chitty run` select (`STATUSES`, `MODE_STATUSES`, and the `todo`-only dependency check in `skip_reason`), which stay as they are; `chitty show`, a `--json` field for planning dependencies, and the rest of `TASK-70`.

Dependency reads are memoised (`src/chitty/store.py`, around line 361), so listing should make no extra Git calls per ticket; `tests/test_list_performance.py` checks that only for `todo` dependents today. Tests use Hypothesis, the repository's property-testing tool. In `tests/test_property_next.py`, add `planning`, `cold-read` and `error` to the test `STATUSES` used by `facts_strategy`, and change the expected `🔒` there to `🔗`.

## Acceptance Criteria

- [ ] Property in `tests/test_property_next.py`: for every fact from `facts_strategy`, `dependency_marker(fact)` equals an independently written expectation (None when archived or `done`; otherwise the first `broken` dependency's message, else `🔗 waits on` the unfinished references, else None), whatever the status. The existing properties pass with `🔗`. It fails on `main` (`dependency_marker` does not exist; stub it raising `NotImplementedError` first). Wrong versions to run and record in a note: one that ignores `broken` dependencies; one that returns None outside a fixed list of statuses.
- [ ] In `tests/test_cli.py`, the list test that builds `Waiting` and `Broken` todo tickets also builds a `planning`, a `cold-read` and a `doing` ticket depending on the unfinished `TASK-1`, a `doing` ticket with owner `agent` depending on `TASK-1`, and a `planning` ticket depending on the missing `TASK-99`. The test lists every expected `chitty list --all` line in full: `🔗` for `Waiting` and the three unowned waiting tickets; `👤` for the owned `doing` ticket; `⚠️` for `Broken` and for the planning ticket on `TASK-99`, each with its own `warning:` line on stderr; the existing lines unchanged except 🔒 becoming 🔗. In `--json`, looked up by `id` rather than index, `skipped` is `"🔗 waits on TASK-1"` for `Waiting`, its `⚠️` text for `Broken`, `"👤 agent"` for the owned `doing` ticket, and `None` for the other four new tickets. It fails on `main`.
- [ ] `tests/test_list_performance.py` also builds `planning` dependents of `TASK-1` and still asserts the same Git call count for both ticket counts. `git grep -n 🔒 -- src tests README.md docs/plan` finds nothing, and `docs/plan/cli.md` says what the Description gives. `make check` passes.

## History

- 2026-11-19T21:45:57Z sunny-white-dormouse → backlog
- 2026-11-19T21:56:42Z sunny-white-dormouse: changed title, description
- 2026-11-19T22:05:12Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T22:05:12Z sunny-white-dormouse backlog → planning
- 2026-11-19T22:05:17Z sunny-white-dormouse planning → cold-read
- 2026-11-19T22:06:11Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T22:06:11Z sunny-white-dormouse cold-read → todo
- 2026-11-19T22:53:24Z sunny-white-dormouse: changed title, description, acceptance criteria
- 2026-11-19T22:53:24Z sunny-white-dormouse todo → planning
- 2026-11-19T22:53:43Z sunny-white-dormouse planning → cold-read
- 2026-11-19T22:54:58Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T22:54:58Z sunny-white-dormouse cold-read → todo
- 2026-11-20T01:09:29Z able-umber-vole todo → doing
