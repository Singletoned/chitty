---
title: Stop `chitty guide cold-read <ID>` when the ticket is not in `cold-read`
status: cold-read
created: 2026-11-25
moved_from: TASK-VKTREF
---

## Description

Seen 2026-11-24 and again 2026-11-25: a planner on a `plan/...` branch started the `cold-reader` subagent with only a ticket ID. The reader ran from the main checkout, read `main`'s older copy (status `backlog`, no criteria), and reported "no Acceptance Criteria" as its top finding, so the read was wasted. Two things cause it:

- `.claude/agents/cold-reader.md` (this repository's Claude Code agent) tells the reader to work in the main checkout.
- `chitty guide cold-read <ID>` (`guide` in `src/chitty/store.py`) never looks at the ticket, so it cannot notice that this checkout's copy is not the one being planned.

Change:

- In `guide`, for the `cold-read` role with an ID, open the repository at `directory`, read the ticket as `chitty show` does (`Repo.find_for_show`), and if its status is not `cold-read`, raise `ChittyError` with `<ID> is <status> in this checkout, not cold-read; run this in the checkout where it is being planned (see git worktree list)`.
- In `.claude/agents/cold-reader.md`, step 1: work in the checkout the prompt names; if it names none, the main checkout. If the guide command refuses, stop and report the message.

No other role changes.

Out of scope: warning `chitty show` readers about newer copies on other branches (TASK-602).

## Acceptance Criteria

- [ ] A Hypothesis property test over every status in `src/chitty/model.py`'s status list: with one ticket in that status, `chitty guide cold-read <ID>` prints the cold-read guide when the status is `cold-read`, and otherwise exits 1 with `<ID> is <status> in this checkout, not cold-read`, printing no guide. Fails today: the guide prints for every status.
- [ ] Regression tests: the existing guide tests pass, including `chitty guide cold-read` with no ID; `make check` passes.

## History

- 2026-11-25T22:28:28Z calm-ochre-quail → backlog
- 2026-11-25T22:28:30Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:23Z calm-ochre-quail: changed title, notes
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-VKTREF
- 2026-11-25T23:49:13Z calm-ochre-quail: replaced notes; changed description, acceptance criteria
- 2026-11-25T23:49:13Z calm-ochre-quail backlog → planning
- 2026-11-25T23:49:23Z calm-ochre-quail planning → cold-read
