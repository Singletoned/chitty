---
title: Add `--mode` to `chitty next` and `chitty run`
status: todo
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

Add `--mode work` and `--mode review` to `chitty next` and `chitty run`. `review` selects only among tickets in `review`, and `work` only among `doing` and `todo`, each in the existing order. With no `--mode`, both behave as they do now. Put the filter in `next_action` in `src/chitty/store.py`, so `run` and `cli.py` stay thin. Add a keyword-only `mode: Literal["work", "review"] | None = None` to `next_action`, which has many callers that want the default, and a `mode` parameter to `run` in `src/chitty/run.py`, passed from the `--mode` option in `src/chitty/cli.py`. `next_action` already has a local called `mode`, so rename that. `chitty next` does not forward arguments, so it only needs the plain option. `TASK-138` adds a `ticket` parameter to `run`, and whichever lands second rebases. When nothing matches, the error says `no next ticket for --mode review`, which keeps the words tests assert, and names the mode, so a person can tell an idle reviewer from a broken one. It still exits non-zero. Declaring the option means `chitty run` no longer forwards a `--mode` to the agent, and `click.Choice` rejects other values. Leave `src/chitty/mcp.py` on the default. In `next_action`, filter before checking dependencies, so a bad reference on a ticket in the other mode does not stop this run.

Split from `TASK-162` on 2026-11-05 so this can land first: it lets a person choose a reviewer's model today, as in `chitty run --mode review -- --model gpt-5.6-terra`. Running the two modes at the same time is `TASK-162`, which needs `TASK-163` and `TASK-164`, so the documentation says to run them one after the other until it lands.

Not in scope: `--mode` alongside `--ticket` from `TASK-138`, which is refused by whichever of the two lands second.

## Acceptance Criteria

- [ ] Tests show `--mode review` and `--mode work` each selecting only their own tickets, in both `chitty next` and `chitty run`, with no `--mode` unchanged, and a message naming the mode when nothing matches
- [ ] `README.md` and `PLAN.md` describe the option, and say to run the modes one after the other until `TASK-162` lands

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. No serious faults: it ran click and confirmed `--mode` before or after forwarded arguments, `--mode=review`, and rejection of other values. Fixed: how the option reaches `next_action` and `run`, and the clashing local. Rejected: abbreviations such as `--mo review` being forwarded, which is what forwarding means.

## History

- 2026-11-05T14:13:49Z mellow-newt → backlog
- 2026-11-05T14:23:08Z mellow-newt: changed description, notes
- 2026-11-05T14:23:09Z mellow-newt backlog → todo
