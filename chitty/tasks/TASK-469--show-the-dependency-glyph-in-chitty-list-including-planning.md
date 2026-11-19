---
title: Show the 🔗 dependency glyph in `chitty list`, including `planning` and `cold-read` tickets
status: planning
parent: TASK-70
created: 2026-11-19
---

## Description

Seen 2026-11-19: `TASK-450` is in `planning` with `depends_on: TASK-426`, but `chitty list` shows nothing in its marker column, so a planner cannot see that it waits on another ticket. The column shows `skip_reason` (`src/chitty/selection.py`): why `chitty next`/`chitty run` would skip a ticket. That returns `None` for any status outside `review`, `doing` and `todo`, and `_selection_facts` (`src/chitty/store.py`) reads dependencies only for `todo`. A slice of `TASK-70` criterion 1.

Decisions:

- The dependency glyph changes from 🔒 to 🔗 (owner, 2026-11-19, recorded on `TASK-70`: one code point, always two columns wide). Add the module constant `DEPENDENCY_GLYPH = "🔗"` in `src/chitty/selection.py` and use it in `skip_reason`'s `waits on` text.
- `skip_reason` and `choose` keep their meaning: they are about selection. `chitty next`, `chitty run` and `chitty list --json` (`skipped`) do not change, apart from the glyph.
- New pure function in `src/chitty/selection.py`: `dependency_marker(fact: TicketFacts) -> str | None`. It returns `None` unless `fact.status` is `planning` or `cold-read` and the ticket is not archived. Then, checking `fact.dependencies` in order: the first `broken` one gives exactly the text `skip_reason` gives for a broken dependency (`⚠️ <ID> depends on <reference>: <error>`); otherwise any `unfinished` ones give `🔗 waits on <references joined by ", ">`; otherwise `None`.
- `_selection_facts` reads dependencies when `dependencies` is true and the status is `todo`, `planning` or `cold-read` (today only `todo`).
- New `list_marker(repo: Repo, stored: StoredTask) -> str | None` in `src/chitty/store.py`: `skip_reason(repo, stored)` if that is not `None`; otherwise, for a `planning` or `cold-read` ticket, `dependency_marker` of `_selection_facts(repo, stored, locked=<as skip_reason reads it>, dependencies=True)`; otherwise `None`. The text output of `chitty list` (`src/chitty/cli.py`) uses `list_marker` instead of `skip_reason` for its marker column and its broken-dependency `warning:` line; its `--json` branch keeps `skip_reason`.
- Docs: replace 🔒 with 🔗 in `README.md` (line 96), `docs/plan/cli.md` (lines 46 and 50) and `docs/plan/next-action-and-runner.md` (line 16); in `docs/plan/cli.md`, say that `planning` and `cold-read` tickets show 🔗 or ⚠️ for their dependencies too.
- Out of scope: `chitty show`, a `--json` field for planning dependencies, and the rest of `TASK-70`.

Tests use Hypothesis, the repository's property-testing tool. In `tests/test_property_next.py`, add `planning` and `cold-read` to the test `STATUSES` used by `facts_strategy`, and change the expected `🔒` there to `🔗`.

## Acceptance Criteria

- [ ] Property in `tests/test_property_next.py`: for every fact from `facts_strategy`, `dependency_marker(fact)` equals an independently written expectation (None unless the status is `planning` or `cold-read` and not archived; then the first `broken` dependency's message, else `🔗 waits on` the unfinished references, else None), and `skip_reason(fact)` is None for every `planning` or `cold-read` fact. The existing properties pass with `🔗`. It fails on `main` (`dependency_marker` does not exist; stub it raising `NotImplementedError` first). Wrong version to run and record in a note: one that ignores `broken` dependencies.
- [ ] In `tests/test_cli.py`, the list test that builds `Waiting` and `Broken` todo tickets also builds a `planning` and a `cold-read` ticket depending on the unfinished `TASK-1`, and a `planning` ticket depending on the missing `TASK-99`. `chitty list --all` shows `🔗` for `Waiting` and both waiting planning tickets, `⚠️` for the broken one with its `warning:` line on stderr, and the expected lines change only by 🔒 becoming 🔗 and the new tickets; `--json` gives `skipped` `"🔗 waits on TASK-1"` for `Waiting` and `None` for the planning and cold-read tickets. It fails on `main`.
- [ ] `git grep -n 🔒 -- src tests README.md docs/plan` finds nothing, and `docs/plan/cli.md` says that `planning` and `cold-read` tickets show their dependencies. `make check` passes.

## History

- 2026-11-19T21:45:57Z sunny-white-dormouse → backlog
- 2026-11-19T21:56:42Z sunny-white-dormouse: changed title, description
- 2026-11-19T22:05:12Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T22:05:12Z sunny-white-dormouse backlog → planning
