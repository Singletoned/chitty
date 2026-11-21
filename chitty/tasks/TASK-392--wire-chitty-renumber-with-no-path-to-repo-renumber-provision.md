---
title: Wire `chitty renumber` with no path to `Repo.renumber_provisional`
status: planning
depends_on:
  - TASK-517
parent: TASK-376
created: 2026-11-18
---

## Description

`Repo.renumber_provisional()` (`TASK-391`) gives provisional tickets sequential numbers on `main`. Expose it as `chitty renumber` with no path, an idempotent command a person or script can run at any time (decided with the owner: renumbering is cosmetic). Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-391` lands.

Decisions:

- `PATH` becomes optional on `chitty renumber` in `src/chitty/cli.py`. Without it, call `renumber_provisional()`. With it, behaviour, output and `--json` keys (`renumbered_dict`) are unchanged.
- Every non-error outcome without `PATH` exits 0: renumbered, nothing to renumber, or off `main`. Other errors (duplicate provisional IDs, an unparseable ticket file, an invalid `chitty.toml` on any branch) exit 1 through the usual handler. Outside a Git repository it renumbers, as `TASK-391` treats that as on `main`.
- Without `PATH`: print one `renumbered <old ID> -> <new ID> <path>` line per ticket; with none, print `nothing to renumber`. `renumber_provisional` raises `ProvisionalOffMain`, a `ChittyError` subclass in `src/chitty/errors.py` defined by `TASK-391`, when off `main`; `renumber` catches only that type, prints `provisional tickets are renumbered on main; nothing changed` to stderr and exits 0. Any other `ChittyError` still exits 1 through the usual handler. `nothing to renumber` also goes to stderr, as the idle-queue message does; `renumbered` lines go to stdout, naming the new file's absolute path, as `_report` prints `change.task.path`. With `--json`, stdout carries only the JSON, and both messages still go to stderr.
- `--json` without `PATH` prints a list of `task.as_dict()` items, as `archive` with no ID does (each `moved_from` holds the old ID), and `[]` when there are none, including off `main`, where the message still goes to stderr.
- The MCP `renumber(path)` tool in `src/chitty/mcp.py` is unchanged; no new MCP tool (`tests/test_mcp.py` pins the tool list).
- The first line of `chitty renumber --help` becomes `Renumber provisional tickets on main, or one of several files sharing an ID.`; update `tests/test_renumber.py` `test_help`, which pins the first line. In `docs/plan/cli.md`, describe `renumber` with no `PATH`: the stdout line, the two stderr messages, exit 0, and the `--json` list.

Tests: CLI tests in `tests/test_renumber_provisional.py` (`TASK-391`'s file). Set `autocommit = true` in the test's `chitty.toml`, run `git init -b main`, set `user.name` and `user.email`, and make an initial commit on `main`; make provisional tickets with `chitty add` on branch `feature`, then `git switch main` and `git merge feature`. The file's CLI tests inherit `CliTestCase` from `tests/test_cli.py` (for `run_cli`; `TASK-391`'s `RepoTestCase` tests may live beside them in another class). The property builds a fresh repository inside each example (in its own `tempfile.mkdtemp(dir=self.tmp)`), `os.chdir`s into it and back afterwards, since `CliTestCase.setUp` changes into `self.root` once per test. It draws 0 to 3 provisional tickets, each active or archived, optionally one mentioning another. A Hypothesis property for idempotence: for 0 to 3 provisional tickets (small `max_examples`, `deadline=None`), the first run prints exactly that many `renumbered` lines to stdout and the second prints `nothing to renumber` to stderr and leaves every file byte-identical.

## Acceptance Criteria

- [ ] Idempotence property passes (it fails on the unchanged code, where `PATH` is required); with two provisional tickets on `main`, the first `chitty renumber` prints one `renumbered <old ID> -> <new ID> <absolute new path>` line each to stdout and exits 0; outside a Git repository it does the same
- [ ] On `feature`, and on a detached `HEAD`, `chitty renumber` prints `provisional tickets are renumbered on main; nothing changed` to stderr, exits 0, and leaves ticket file bytes and `git status` unchanged; with an invalid `chitty.toml`, on `main` or on `feature`, it exits 1 with the config error
- [ ] `chitty renumber --json` with two provisional tickets lists both, each with its new ID and `moved_from` the old one; it prints `[]` when nothing changes and off `main`
- [ ] Regression guards: `tests/test_renumber.py` (with `test_help` expecting the new first line) and `tests/test_mcp.py` `test_tools_mirror_the_cli` pass; `docs/plan/cli.md` lists, for `renumber` with no `PATH`, the stdout line, both stderr messages, exit 0 and the `--json` list; `make check` passes

## Notes

The store method moved to `TASK-517`, which depends on the preflight `TASK-391`. Update this ticket against the landed store behavior and cold-read it before moving it back to `todo`.

## History

- 2026-11-18T16:37:33Z lively-quartz-crane → backlog
- 2026-11-18T16:37:39Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:37:39Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:40Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:42:17Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:42:17Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:44:51Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:46:21Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:46:21Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:48:26Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:49:45Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:49:45Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:49:47Z lively-quartz-crane planning → todo
- 2026-11-21T18:37:19Z eager-ginger-adder: changed dependencies, notes
- 2026-11-21T18:37:19Z eager-ginger-adder todo → planning
