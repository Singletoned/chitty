---
title: Reduce actor-name collisions and keep one name per run loop
status: backlog
created: 2026-11-11
---

## Description

Observed in echonomicon on 2026-11-11. An agent recorded a `doing → review` move on TASK-98 as `sunny-jay`, which is also the name of an unrelated Claude Code session. Separately, TASK-85 was blocked because a reviewer's criterion ticks counted as work. The name space is 25 × 25 = 625 (`actor.py` `_readable_name`, two bytes of SHA-256). `chitty run` hashes a fresh `uuid4()` per attempt (`run.py:116`), and `run_loop` starts a new process per ticket, so a busy day creates many actors. With about 30 actors in a repo, the chance that some pair shares a name is about 50%. Review independence relies on names being distinct, both ways: a false clash refuses a legitimate review, and a real clash would let an implementer review its own work.

Suggestions, cheapest first:

1. Fix review edits counting as work. Ticking criteria and adding notes during review currently makes the reviewer count as having worked on the ticket (TASK-85 in echonomicon: "Chitty rejected the review transition ... because the review edit ticked acceptance criteria"). This blocks failed reviews today, and it would block every re-review once names are long-lived (point 3).
2. Three-part names (adjective-adjective-animal, or adding a second animal list) give 15,625 combinations, a one-line change with no state. At 30 actors the chance of any clash drops to about 3%. Adding words to the lists also helps.
3. One name per `chitty run --loop`: have `run_loop` choose the name once and pass it to each child through an environment variable (for example `CHITTY_RUN_ACTOR`), which `run()` uses instead of a new uuid. This is about 10 lines. A loop without `--mode` (work and review) would then need `chitty next` to skip review of tickets that actor worked on. A name per terminal (across separate invocations) could use `TERM_SESSION_ID` where it is set, but that is not portable.
4. Avoid recently used names for `chitty run`: its names are random anyway, so pick one not seen in recent ticket history (for example the last 7 days of history lines, which chitty already parses). This is about 20 lines. Doing the same for harness sessions (Claude, Pi, Codex), whose names are recomputed statelessly from session IDs, would need a small stored map of identity to name under `~/.local/share/chitty/`.

## Notes

Suggestion origin: echonomicon

Split 2026-11-11 into TASK-285 (three-part names), TASK-286 (review edits are not work) and TASK-287 (one name per loop). Point 4, avoiding recent names, is left out: three-part names make clashes rare enough.

## History

- 2026-11-11T16:08:27Z vivid-yellowhammer → backlog
- 2026-11-11T16:08:27Z vivid-yellowhammer: changed notes
- 2026-11-11T16:09:07Z vivid-yellowhammer: changed notes
