---
title: Tell work and repair agents to finish a stopped rebase
status: planning
priority: high
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

When the runner's rebase stops on a code conflict, the agent finishes it (`TASK-370` for work, `TASK-375` for review). It needs instructions. Nothing can be written to the ticket during a stopped rebase, so they come from the guide itself.

Decisions:

- New role file `src/chitty/roles/rebase.md`, printed by `chitty guide rebase <ID>`. It says: a rebase onto the integration branch stopped on conflicts; resolve each conflicted file keeping the intent of both sides; `git add` it; run `git -c core.editor=true rebase --continue`; repeat until no rebase is in progress; never run `git rebase --abort` or `--skip`; then run the configured setup and check commands and fix what the rebase broke. Keep it general (no repository-specific advice), as `AGENTS.md` requires of the guides.
- Add `rebase` to `ROLE_NAMES` in `src/chitty/store.py`, and to the role list in the `guide` command's help in `src/chitty/cli.py`; it takes a ticket ID like `work`.
- `guide()` in `src/chitty/store.py` gains a `directory: Path` argument (no default): the checkout whose state it reads. The CLI and MCP pass the current directory. The runner's `_agent_command` in `src/chitty/run.py` passes the ticket worktree, since the runner's own directory is the main checkout. This ticket makes that change, so `TASK-370` only relies on it.
- For roles `work` and `repair`, when `git.is_repository(directory)` and `git.rebase_in_progress(directory)` are both true, insert the `rebase` role text, followed by a blank line, directly after the `Work only on Chitty ticket <ID>.` line and before the role's usual text. Outside a repository there is no rebase, so nothing is added; any Git error inside a repository raises as usual.

Tests: in a new `tests/test_guide_rebase.py`, calling `guide()` and the CLI, with real repositories: a rebase stopped on a real conflict, with both backends (`rebase-merge` by default and `rebase-apply` with `git rebase --apply`), from the worktree root and from a subdirectory, and from a linked worktree; a clean repository; and a directory outside any repository. The oracle for "unchanged" is that, with no rebase in progress, the output equals the stopped-rebase output with the inserted rebase text and its blank line removed, and equals the output outside a repository. No property: a fixed set of states and two guides, all listed.

## Acceptance Criteria

- [ ] `chitty guide rebase TASK-<n>` prints the `rebase` role text, which names `git rebase --continue` and forbids `--abort` and `--skip`
- [ ] With a rebase stopped on a conflict (both backends, root and subdirectory, linked worktree), the work and repair guide output has the rebase text directly after the `Work only on Chitty ticket <ID>.` line; the test fails before the change
- [ ] With no rebase in progress, or outside a repository, the work and repair guides equal the stopped-rebase output with the rebase text and its blank line removed
- [ ] The runner passes the ticket worktree: a work run whose worktree has a stopped rebase gives the fake agent a prompt containing the rebase text, though the main checkout has none; `make check` passes

## History

- 2026-11-18T09:50:54Z witty-ginger-falcon → planning
- 2026-11-18T09:52:32Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:55:11Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:55:13Z witty-ginger-falcon: changed description, acceptance criteria
