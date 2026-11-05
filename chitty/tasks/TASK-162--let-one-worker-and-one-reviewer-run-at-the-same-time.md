---
title: Let one worker and one reviewer run at the same time
status: todo
priority: high
depends_on:
  - TASK-163
  - TASK-164
  - TASK-186
parent: TASK-106
created: 2026-11-04
---

## Description

The human asked for this on 2026-11-04: running one worker and one reviewer together should already be fairly safe. A cold read found that selection is the main obstacle but not the only one: `TASK-163` and `TASK-164` fix the silent failures first. `chitty next` always takes `review` first, then `doing`, then `todo`, so two runs pick the same ticket.

`TASK-186` adds `--mode work` and `--mode review`. The sets do not overlap at the moment of selecting, so one run of each cannot start on the same ticket. A ticket that fails review moves to `doing` and may be taken by the worker while the reviewer's session is ending, sharing its worktree briefly, which is accepted.

The test for overlapping sessions runs real `chitty run` subprocesses, because `run` changes `os.environ` and the tests change directory. To avoid timeouts, the outer run is `chitty run --mode work`, and its fake agent starts the `--mode review` run itself and waits for it to finish, so the two are guaranteed to overlap. It finds `chitty` as `Path(sys.executable).parent / "chitty"`, as existing tests do. Before starting, commit the review ticket on its branch, and use `setup = "true"` with a current `chitty_version`, so neither run writes to the main checkout. Configure an `agent_command` containing `{mode}`, so the fake knows which it is.

`test_suggestions_never_change_the_real_inbox` in `tests/test_inbox.py` compares the whole real inbox before and after, so another session's `chitty suggest` would wrongly fail a review. Have it look only for the suggestion it created.

What else the two runs share, for the documentation to state: both write to the main checkout, through setup refresh, inbox pull and the reviewer's merge, and a collision fails loudly on Git's lock or a dirty file, so rerun it. Two branches bumping to the same `__version__` merge without a conflict, so one change may not get its own version; this is accepted, and `TASK-108` holds a candidate check. Replace the sentence `TASK-186` added to `README.md` and `PLAN.md`, saying to run the modes one after the other. `PLAN.md`'s "at most one ticket is in `work` at a time, merged before the next starts" must change to say one worker and one reviewer.

Not in scope: two workers or two reviewers, because the claim is not atomic; and a loop that waits for tickets.

## Acceptance Criteria

- [ ] `README.md` and `PLAN.md` describe running one of each, including what a collision looks like, and the inbox test no longer reads other sessions' suggestions

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. It tested the claim that only selection stands in the way, and found that claim wrong. Moved to their own tickets: a dependency counted as done before it reaches `main`, and `historical_files` hiding Git errors, both silent. Fixed here: the inbox test, which could wrongly fail a review; an overlap test with no timeouts; the error text; and the contradiction in `PLAN.md`. Accepted and to be documented: loud collisions in the main checkout, and two branches sharing a version. Rejected: a stale index after a failed rollback, which is speculative; `~/.pi` extension rewrites, which happen only on a version change at start; concurrent `CHITTY_USAGE_FILE` writes, because `TASK-127` gives each run its own file; and a separate ticket for the overlap test, which the simpler design no longer needs.

Second cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the error text, filtering before dependency checks, and how the overlap test is set up. Rejected: its suggestion to split, because the nested test needs no handshake or timeout, so it stays small; and `--mode` in MCP, which nothing needs yet. `--ticket` refusal stays with whichever of this and `TASK-138` lands second.

Split on 2026-11-05: selection with `--mode` moved to `TASK-186`, so a person can use it before the concurrency work. This ticket keeps the overlap test, the inbox test and the documentation.

## History

- 2026-11-04T20:15:22Z mellow-newt → backlog
- 2026-11-04T20:20:09Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T20:22:55Z mellow-newt: changed description, notes
- 2026-11-04T20:22:56Z mellow-newt backlog → todo
- 2026-11-05T10:07:37Z mellow-newt: changed description
- 2026-11-05T10:23:49Z mellow-newt: changed description
- 2026-11-05T14:13:50Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-05T14:23:11Z mellow-newt: changed description, acceptance criteria
