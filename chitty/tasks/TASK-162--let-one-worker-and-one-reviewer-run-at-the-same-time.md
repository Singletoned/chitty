---
title: Let one worker and one reviewer run at the same time
status: backlog
priority: high
depends_on:
  - TASK-163
  - TASK-164
parent: TASK-106
created: 2026-11-04
---

## Description

The human asked for this on 2026-11-04: running one worker and one reviewer together should already be fairly safe. A cold read found that selection is the main obstacle but not the only one: `TASK-163` and `TASK-164` fix the silent failures first. `chitty next` always takes `review` first, then `doing`, then `todo`, so two runs pick the same ticket.

Add `--mode work` and `--mode review` to `chitty next` and `chitty run`. `review` selects only among tickets in `review`, and `work` only among `doing` and `todo`, each in the existing order. The sets do not overlap at the moment of selecting, so one run of each cannot start on the same ticket. A ticket that fails review moves to `doing` and may be taken by the worker while the reviewer's session is ending, sharing its worktree briefly, which is accepted. With no `--mode`, both behave as they do now. Put the filter in `next_action` in `src/chitty/store.py`, so `run` and `cli.py` stay thin. When nothing matches, the error says `no next ticket for --mode review`, which keeps the words tests assert, and names the mode, so a person can tell an idle reviewer from a broken one. It still exits non-zero. Declaring the option means `chitty run` no longer forwards a `--mode` to the agent, and `click.Choice` rejects other values. Leave `src/chitty/mcp.py` on the default. In `next_action`, filter before checking dependencies, so a bad reference on a ticket in the other mode does not stop this run.

The test for overlapping sessions runs real `chitty run` subprocesses, because `run` changes `os.environ` and the tests change directory. To avoid timeouts, the fake work agent starts the `--mode review` run itself and waits for it to finish, so the two are guaranteed to overlap. It finds `chitty` as `Path(sys.executable).parent / "chitty"`, as existing tests do. Before starting, commit the review ticket on its branch, and use `setup = "true"` with a current `chitty_version`, so neither run writes to the main checkout. Configure an `agent_command` containing `{mode}`, so the fake knows which it is.

`test_suggestions_never_change_the_real_inbox` in `tests/test_inbox.py` compares the whole real inbox before and after, so another session's `chitty suggest` would wrongly fail a review. Have it look only for the suggestion it created.

What else the two runs share, for the documentation to state: both write to the main checkout, through setup refresh, inbox pull and the reviewer's merge, and a collision fails loudly on Git's lock or a dirty file, so rerun it. Two branches bumping to the same `__version__` merge without a conflict, so one change may not get its own version; this is accepted, and `TASK-108` holds a candidate check. `PLAN.md`'s "at most one ticket is in `work` at a time, merged before the next starts" must change to say one worker and one reviewer.

Not in scope: two workers or two reviewers, because the claim is not atomic; a loop that waits for tickets; and `--mode` alongside `--ticket` from `TASK-138`, which should be refused if both have landed.

## Acceptance Criteria

- [ ] Tests show `--mode review` and `--mode work` each selecting only their own tickets, in both `chitty next` and `chitty run`, with no `--mode` unchanged and a message naming the mode when nothing matches
- [ ] A test using real `chitty run` subprocesses overlaps a work session and a review session on different tickets, and both report the right status with different actors
- [ ] `README.md` and `PLAN.md` describe running one of each, including what a collision looks like, and the inbox test no longer reads other sessions' suggestions

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. It tested the claim that only selection stands in the way, and found that claim wrong. Moved to their own tickets: a dependency counted as done before it reaches `main`, and `historical_files` hiding Git errors, both silent. Fixed here: the inbox test, which could wrongly fail a review; an overlap test with no timeouts; the error text; and the contradiction in `PLAN.md`. Accepted and to be documented: loud collisions in the main checkout, and two branches sharing a version. Rejected: a stale index after a failed rollback, which is speculative; `~/.pi` extension rewrites, which happen only on a version change at start; concurrent `CHITTY_USAGE_FILE` writes, because `TASK-127` gives each run its own file; and a separate ticket for the overlap test, which the simpler design no longer needs.

Second cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the error text, filtering before dependency checks, and how the overlap test is set up. Rejected: its suggestion to split, because the nested test needs no handshake or timeout, so it stays small; and `--mode` in MCP, which nothing needs yet. `--ticket` refusal stays with whichever of this and `TASK-138` lands second.

## History

- 2026-11-04T20:15:22Z mellow-newt → backlog
- 2026-11-04T20:20:09Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T20:22:55Z mellow-newt: changed description, notes
