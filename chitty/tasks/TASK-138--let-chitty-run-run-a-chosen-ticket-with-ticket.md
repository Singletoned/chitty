---
title: Let `chitty run` run a chosen ticket with `--ticket`
status: backlog
priority: high
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-04
---

## Description

`chitty run` always takes what `chitty next` selects, so a person cannot choose. Add `chitty run --ticket <ID>`, which runs that ticket instead of the selected one, in the mode its status implies: `review` means review, and `doing` or `todo` means work. Everything else about the run is unchanged, including the inbox pull, worktree preparation and forwarding other arguments to the agent. Resolve the ID after the pull, on `main_repo`, with `Repo.resolve`, so `13` and `TASK-13` both work and a pulled ticket can be chosen.

Declare it with `click.option("--ticket", metavar="ID", help=...)`, so it appears in the help text, and have the command's docstring say that it runs the next ticket, or the one named by `--ticket`, and that other arguments go to the agent. Give `run()` in `src/chitty/run.py` a parameter `ticket: str | None`, without a default; Where `run` calls `next_action(main_repo)`, after the inbox pull and before `_agent_command`, call the new function instead when it is set, and update the call in `src/chitty/cli.py`, which is the only caller. Use an option rather than a positional argument. `chitty run` forwards unknown arguments to the agent, so a positional would be confused with those, as in `chitty run -e ./search.ts`.

Add a function beside `next_action` in `src/chitty/store.py` that returns a `NextAction` for a given ticket, factoring the per-ticket check out of the loop in `next_action` rather than copying it, so a bad `depends_on` reference raises the same error, even on a `doing` or `review` ticket; `run` and `cli.py` stay thin. It refuses, with a message saying why, and before any claim or worktree: an unknown or archived ticket, checked explicitly because `repo.find` returns archived tickets; a status other than `review`, `doing` or `todo`; a `human` ticket or owner; and a `todo` ticket whose dependencies are not `done`. As in `next_action`, `doing` and `review` tickets are not held back by dependencies. Choosing a ticket overrides priority and order only: the rules exist because the work would fail or belongs to someone else. To override one, change the ticket first.

Depends on `TASK-126`, which changes the command and `src/chitty/run.py`. `TASK-152` lands pending tickets at the start of a run; a run with `--ticket` skips that, because it must only touch that ticket.

Out of scope: an option on `chitty next`, running several tickets, and overriding the refusals above. `--mode` from `TASK-162` with `--ticket` is refused by whichever of the two lands second.

## Acceptance Criteria

- [ ] Tests show each refused case failing with a message saying why, with no claim and no worktree created
- [ ] `README.md` and `PLAN.md` describe the option, and a test shows `chitty run --help` listing `--ticket` and its description saying it runs the next ticket or the named one
- [ ] A test with a fake agent shows `--ticket` running a lower-priority `todo` ticket in work mode ahead of what `chitty next` selects, a `review` ticket in review mode, and a `doing` ticket with unfinished dependencies in work mode
- [ ] A test shows other arguments still reaching the agent with `--ticket` before or after them, a bare number resolving, and `chitty run` without the option behaving as before

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the inbox pull still runs, and the ID resolves after it; bare numbers; the archived check being explicit; how the rules are shared; and `doing` tickets with unfinished dependencies being allowed, now tested. It ran click with these settings and confirmed `--ticket` works before or after forwarded arguments, and `--ticket=ID` too. Rejected: a `doing` ticket with no branch, because `_worktree` creates one, as for any selected ticket. A `doing` worktree held by another live session, because a single worker is the stated assumption and nothing checks liveness today; a person choosing a ticket is responsible for that. `--tick 7` being forwarded rather than matched, and `--ticket` after `--` reaching the agent, because both are what forwarding means. A missing option value, because click reports it. A test that `TASK-120` and `TASK-131` leave other tickets alone, because neither has landed; the description tells whichever lands second. The function name and refusal wording, which are the worker's choice.

Landing at the start of a run is now `TASK-152`, so that is the ticket that must only touch the chosen one.

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: this named the wrong tickets after the split.

Changed 2026-11-05 at the human's request: they asked for `chitty run TASK-178`, not `--ticket`, with it in the help text, and it is now high priority. The earlier objection to a positional argument still holds for a declared one, so this reads only a first word shaped like an ID. Earlier notes describe `--ticket`.

Held in `backlog` while the rewrite is cold-read.

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: a criterion still saying `--ticket`, which I knew about; how the ID reaches `run()`, so it is not forwarded too; loose help wording; and `gpt-4` matching `ID_RE`. The report accepted refusing that as an unknown ticket, but I required a known prefix instead, so model names are forwarded. Not split: four criteria.

Back to `--ticket` on 2026-11-05: the human prefers it, and `chitty run TASK-178` was the planning session's suggestion, not theirs. The note before this and the positional design are superseded. Kept from that rewrite: the help text the human asked for, how the ID reaches `run()`, the `--mode` refusal, and high priority. The earlier cold read of `--ticket` still applies; nothing else changed.

Held in `backlog` for a cold read of the restored `--ticket` design.

## History

- 2026-11-04T09:46:25Z lively-panda → todo
- 2026-11-04T09:47:28Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T15:11:40Z mellow-newt: changed notes
- 2026-11-04T15:17:42Z mellow-newt: changed description, notes
- 2026-11-05T10:07:30Z mellow-newt: changed description
- 2026-11-05T10:07:31Z mellow-newt: changed title, priority, acceptance criteria
- 2026-11-05T10:07:32Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T10:07:45Z mellow-newt: changed notes
- 2026-11-05T10:07:45Z mellow-newt todo → backlog
- 2026-11-05T10:08:34Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T10:08:35Z mellow-newt: changed acceptance criteria
- 2026-11-05T10:08:36Z mellow-newt: changed acceptance criteria
- 2026-11-05T10:08:37Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T10:08:38Z mellow-newt backlog → todo
- 2026-11-05T10:23:38Z mellow-newt: changed title, description
- 2026-11-05T10:23:38Z mellow-newt todo → backlog
- 2026-11-05T10:23:39Z mellow-newt: changed acceptance criteria
- 2026-11-05T10:23:40Z mellow-newt: changed acceptance criteria
- 2026-11-05T10:23:41Z mellow-newt: changed acceptance criteria
- 2026-11-05T10:23:42Z mellow-newt: changed acceptance criteria
- 2026-11-05T10:23:43Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T10:23:44Z mellow-newt backlog → todo
- 2026-11-05T10:27:41Z mellow-newt: changed notes
- 2026-11-05T10:27:41Z mellow-newt todo → backlog
- 2026-11-05T10:28:41Z mellow-newt: changed description
