---
title: Show later versions from other branches in `show` and `list` on `main`
status: backlog
depends_on:
  - TASK-604
created: 2026-11-23
---

## Description

Decided with the person, 2026-11-26 (see `docs/plan/principles.md`): on `main`, Chitty gives the best view it can of the whole situation. `show` and `list` read `main`'s copy of a ticket and also every later version on other local or remote-tracking branches, of which there may be several, and which may be stale. Today only the ticket's own `task-<n>` branch is read, and `show` prints one chosen copy.

To be planned, probably as more than one ticket:

- `show` on `main`: print `main`'s copy (or the chosen one), then one line per branch with a later version, naming the branch and its status there.
- `list` on `main`: mark each line that has later versions elsewhere, naming the branch. Settle which status the line shows: today's newest-of-`main`-and-`task-<n>`, which keeps work in progress visible, or `main`'s with the marker.
- `next` and `run`: keep choosing from `main` and `task-<n>` branches only, so a ticket moved to `todo` on an unlanded `plan/` branch is not picked up (TASK-340 relies on that). Confirm when planning.
- The marker's form, `--json`, and tests including a branch behind `main`.

Needs a once-per-command index of the tickets each other branch changed since it split from `HEAD` (one `git diff -z --no-renames --name-only HEAD...<ref>` per ref; 17 refs took 0.19 s in total on 2026-11-23). Plan it as its own ticket, building on the per-branch diffs of TASK-604.

## History

- 2026-11-23T08:22:18Z plucky-umber-wren → todo
- 2026-11-23T08:22:38Z plucky-umber-wren todo → backlog
- 2026-11-23T08:47:34Z plucky-umber-wren: changed title, dependencies, description
- 2026-11-26T18:02:03Z brisk-bronze-adder: changed title, dependencies, description
- 2026-11-26T21:58:17Z youthful-lilac-heron: changed description
