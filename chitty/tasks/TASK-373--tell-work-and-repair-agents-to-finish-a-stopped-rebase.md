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
- `chitty guide work <ID>` and `chitty guide repair <ID>` (the `{prompt}` for work and repair sessions) put the `rebase` role text first, before their usual text, when `git.rebase_in_progress` is true for the current directory, and add nothing otherwise.

Tests: in a new `tests/test_guide_rebase.py`, with a real repository: a stopped rebase (made with a real conflict) makes the work and repair guides start with the rebase text, and with no rebase in progress they are unchanged byte for byte. No property: two fixed states (rebase in progress or not) times two guides, all listed.

## Acceptance Criteria

- [ ] `chitty guide rebase TASK-<n>` prints the `rebase` role text, which names `git rebase --continue` and forbids `--abort` and `--skip`
- [ ] With a rebase stopped on a conflict, `chitty guide work` and `chitty guide repair` output starts with that text; the test fails before the change
- [ ] With no rebase in progress, both guides print exactly what they printed before the change
- [ ] `make check` passes

## History

- 2026-11-18T09:50:54Z witty-ginger-falcon → planning
- 2026-11-18T09:52:32Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:55:11Z witty-ginger-falcon cold-read → planning
