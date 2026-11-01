---
title: Unblock tasks automatically when their last blocker is done
status: backlog
created: 2026-11-01
---

## Description

Nothing in chitty notices when a blocked task's blocker finishes, so blocked chains stay blocked after the work that held them up is done, until someone happens to look.

What happened (circuitry, 2026-11-01): `CIRCUIT-84` has `depends_on: CIRCUIT-82` and status `blocked`. `CIRCUIT-82` went `review` → `done`, but `CIRCUIT-84` stayed `blocked`, with a note still saying "Blocked by `CIRCUIT-82`, which is waiting for the required independent review of `CIRCUIT-81`" (both long since done). Its parent `CIRCUIT-80` is `blocked` on its children and its notes name a `HUMAN-2` wait that was closed days earlier. `chitty check` reported only Markdown-delimiter warnings, and `chitty list -s blocked` gives no hint that either block is stale. The same thing happened earlier with `CIRCUIT-82` and `CIRCUIT-83`, each unblocked by hand once noticed.

Proposal:

1. When `chitty edit X -s done` (or `archive`) completes a task, find every `blocked` task that lists `X` in `depends_on`, or is `X`'s parent. If all of its dependencies (and, for a parent, all children) are now `done`, move it back to the status it had before `blocked` (its History records this, usually `todo`) and append a note such as "Unblocked: `CIRCUIT-82` is done." Print each unblocked ID so the agent sees what is newly workable.
2. A parent whose children are done but which is not itself done should go to `review` (or whatever the parent rule is), not `todo`; a parent with some children still open should stay blocked, but its "waits on" should be visible (see the earlier suggestion about showing the ends of blocked chains).
3. `chitty check` warns about a `blocked` task with no open dependency and no open child ("blocked with nothing to wait on"); `chitty fix` applies step 1 to it. This catches blocks made stale by hand edits or by another agent's commit.
4. A `blocked` task with no `depends_on` at all (blocked on something outside the repo) is left alone, since chitty can't know when it clears; the AGENTS.md guidance already says to depend on a `-c human` task in that case, which makes it trackable.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
