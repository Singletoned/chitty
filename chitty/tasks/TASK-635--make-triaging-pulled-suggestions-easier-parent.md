---
title: Make triaging pulled suggestions easier (parent)
status: backlog
created: 2026-11-23
---

## Description

The person asked (2026-11-23) for pulling from the inbox to be made easier. Triaging 20 suggestions on 2026-11-23 showed where the effort went:

1. Finding duplicates by hand. Most of the work was checking each suggestion against existing tickets: 7 of 20 were already done or ticketed (for example TASK-618 was done as TASK-545; TASK-616 duplicated TASK-424 and TASK-487). This needed many `chitty list --all` and title greps.
2. Discarding a duplicate takes a note plus `chitty archive` per ticket, with no status that says "not doing this" (TASK-599 adds `dropped`).
3. Pulled tickets keep the raw suggestion title, sometimes a sentence or a pasted path (for example `Running check in /Users/.../task-4... isn't very helpful...`), and every one needs retitling while planning.
4. Each `chitty list` took about 12 seconds in this repository (TASK-598 covers scanning once per command).

Children: show possible duplicates for each suggestion; (later, after TASK-599) let triage drop a duplicate in one command. Keep the command surface small: improve `chitty inbox` and `--pull` output rather than adding commands.

## History

- 2026-11-23T10:41:17Z witty-russet-gannet → backlog
