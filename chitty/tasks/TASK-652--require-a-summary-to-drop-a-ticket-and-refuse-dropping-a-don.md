---
title: Require a Summary to drop a ticket, and refuse dropping a `done` one
status: planning
labels:
  - needs-minor
priority: high
depends_on:
  - TASK-599
parent: TASK-599
created: 2026-11-24
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close a ticket is `done`, which (with review on) needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. On 2026-11-22 an agent asked to close the superseded `TASK-451` that way was stopped by its own permission check as faking a review; the ticket is still open. Add a terminal status for tickets that will not be done.

Split from `TASK-599` on 2026-11-24; `TASK-599` adds the `dropped` status, and this ticket adds the rules for dropping a ticket with `chitty edit`. The `chitty add` refusal is `TASK-653`.

Decisions:

- `chitty edit <id> -s dropped` is allowed from every status except `done` (`dropped` from `done` raises `ChittyError` `<id> is done; it cannot be dropped`), and never needs `review`. It needs a reason: after the edit is applied, the ticket must have a non-empty Summary section, either set by this edit (`--summary`/`--summary-file`) or already there; a Summary that is empty after stripping whitespace counts as empty (`--summary ""` removes it, so that is refused). Otherwise it raises `ChittyError` `dropping <id> needs a --summary saying why`, and nothing is written. The Summary rule applies to every edit whose resulting status is `dropped`, including edits to a ticket that is already `dropped` with or without `-s`: `--summary ""` on a dropped ticket is refused, and so is any edit (for example `--note x`) to a dropped ticket that has no Summary. With a Summary, `-s dropped` on an already dropped ticket is accepted and leaves the status `dropped`, as setting a status to its current value does today. Leaving `dropped` for another status is allowed as for any status (a ticket can be revived); `-s done` from `dropped` follows the review rule it follows today.
- Where the checks live, in `src/chitty/store.py` (`AGENTS.md`: behaviour lives in the store): the `done` refusal, then the Summary rule, in `Repo._edit_stored`, on the task after the edit is applied, stripping the Summary read from the file with `str.strip()` (`model.parse` keeps a whitespace-only Summary as written).
- Locks: `_edit_stored` checks no run lock for any status change today; dropping a `doing` or `review` ticket that a run holds follows the same rule (allowed). Not changed here.

Tests in a new `tests/test_status_dropped.py`, inheriting `CliTestCase` from `tests/test_cli.py` (a `RepoTestCase` whose `run_cli` wraps `click.testing.CliRunner`), as `tests/test_edit_human.py` does; the repository is not a Git repository (no `git init`); it is the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`). Every `done` ticket in a fixture is written directly with `status: done` in its frontmatter, since review is on and `chitty add -s done` is refused:

- From each of `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error` and `review`: `chitty edit TASK-1 -s dropped --summary "Superseded by TASK-2."` exits 0; the file has `status: dropped`, its Summary section is `Superseded by TASK-2.`, and its History has the transition.
- Without `--summary` on a ticket with no Summary: exits non-zero, the output contains `dropping TASK-1 needs a --summary saying why`, and the file is byte-identical to before (the message is what tells this apart from today's invalid-choice error). On a ticket that already has a Summary: exits 0. On a ticket that already has a Summary, `--summary ""`, and on a ticket with no Summary, `--summary "   "`: each refused with the same message, file byte-identical. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 -s dropped` exits 0 and the status stays `dropped`. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 --summary ""` is refused with the same message, file byte-identical. On a `dropped` ticket file written with no Summary, and on one written with a `## Summary` heading followed only by blank and space-only lines, `chitty edit TASK-1 --note x` is refused with the same message, file byte-identical.
- From `done`, with `--summary "x"` (so only the `done` rule can refuse): refused, the output contains `TASK-1 is done; it cannot be dropped`, file byte-identical.

## Acceptance Criteria

- [ ] From each of `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error` and `review`, `-s dropped --summary` gives the stated file (status, Summary, History); from `done` it is refused with its message and the file is unchanged; the refusal fails before the change
- [ ] The summary refusals (none, `""`, whitespace, a whitespace-only Summary in the file), `-s dropped` and `--summary ""` on a dropped ticket, and `--note` on a dropped ticket with no Summary pass, each asserting its message and an unchanged file, and each refusal fails before the change. Record both runs in a note
- [ ] `make check` passes

## History

- 2026-11-24T08:45:25Z sunny-hazel-gannet → planning
- 2026-11-24T08:45:42Z sunny-hazel-gannet: changed description
