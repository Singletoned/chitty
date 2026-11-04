---
title: Let `chitty run` run a chosen ticket with `--ticket`
status: todo
priority: medium
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-04
---

## Description

`chitty run` always takes what `chitty next` selects, so a person cannot choose. Add `chitty run --ticket <ID>`, which runs that ticket instead of the selected one, in the mode its status implies: `review` means review, and `doing` or `todo` means work. Everything else about the run is unchanged, including the inbox pull, worktree preparation and forwarding other arguments to the agent. Resolve the ID after the pull, on `main_repo`, with `Repo.resolve`, so `13` and `TASK-13` both work and a pulled ticket can be chosen.

Use an option rather than a positional argument. `chitty run` forwards unknown arguments to the agent, so a positional would be confused with those, as in `chitty run -e ./search.ts`.

Add a function beside `next_action` in `src/chitty/store.py` that returns a `NextAction` for a given ticket, factoring the per-ticket check out of the loop in `next_action` rather than copying it, so a bad `depends_on` reference raises the same error; `run` and `cli.py` stay thin. It refuses, with a message saying why, and before any claim or worktree: an unknown or archived ticket, checked explicitly because `repo.find` returns archived tickets; a status other than `review`, `doing` or `todo`; a `human` ticket or owner; and a `todo` ticket whose dependencies are not `done`. As in `next_action`, `doing` and `review` tickets are not held back by dependencies. Choosing a ticket overrides priority and order only: the rules exist because the work would fail or belongs to someone else. To override one, change the ticket first.

Depends on `TASK-126`, which changes the command and `src/chitty/run.py`. `TASK-120` and `TASK-131` act on pending tickets at the start of a run, so a run with `--ticket` must only touch that ticket; they should keep to this if they land later, and this ticket should if they land first.

Out of scope: an option on `chitty next`, running several tickets, and overriding the refusals above.

## Acceptance Criteria

- [ ] Tests show each refused case failing with a message saying why, with no claim and no worktree created
- [ ] `README.md` and `PLAN.md` describe the option
- [ ] A test with a fake agent shows `--ticket` running a lower-priority `todo` ticket in work mode ahead of what `chitty next` selects, a `review` ticket in review mode, and a `doing` ticket with unfinished dependencies in work mode
- [ ] A test shows other arguments still reaching the agent with `--ticket` before or after them, a bare number resolving, and `chitty run` without the option behaving as before

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the inbox pull still runs, and the ID resolves after it; bare numbers; the archived check being explicit; how the rules are shared; and `doing` tickets with unfinished dependencies being allowed, now tested. It ran click with these settings and confirmed `--ticket` works before or after forwarded arguments, and `--ticket=ID` too. Rejected: a `doing` ticket with no branch, because `_worktree` creates one, as for any selected ticket. A `doing` worktree held by another live session, because a single worker is the stated assumption and nothing checks liveness today; a person choosing a ticket is responsible for that. `--tick 7` being forwarded rather than matched, and `--ticket` after `--` reaching the agent, because both are what forwarding means. A missing option value, because click reports it. A test that `TASK-120` and `TASK-131` leave other tickets alone, because neither has landed; the description tells whichever lands second. The function name and refusal wording, which are the worker's choice.

Landing at the start of a run is now `TASK-152`, so that is the ticket that must only touch the chosen one.

## History

- 2026-11-04T09:46:25Z lively-panda → todo
- 2026-11-04T09:47:28Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T15:11:40Z mellow-newt: changed notes
