---
title: Ticket-file commits on a ticket branch conflict when rebasing onto main
status: backlog
created: 2026-11-23
---

## Description

Seen in the circuitry repo on 2026-11-22. Branch `circuit-96` held one content commit plus two `chitty: edit CIRCUIT-96` commits that changed the ticket file (status doing to review, notes, ticked criteria). Meanwhile `main` received its own `chitty: edit CIRCUIT-96` commit (runner error note, status error). `git rebase main` stopped with a conflict in `chitty/tasks/CIRCUIT-96--*.md`. The fix was to reset the branch to main, cherry-pick only the content commit, and redo the ticket edit on main. Because AGENTS.md now says to rebase ticket branches onto main before checks, this will recur whenever the runner and a worker both edit the ticket. Possible fixes: keep ticket state edits only on main, or have `chitty run` resolve ticket-file conflicts automatically (for example by taking main and replaying the field changes through chitty). Separately, four worker runs and one reviewer run on 2026-11-14 all ended with "<ID> was unchanged; only committed changes are visible to `chitty run`" and recorded no cause; capturing the agent exit status or log in the note would make these diagnosable.

## Notes

Suggestion origin: circuitry

Duplicate of TASK-340 and TASK-497; diagnostics half folded into TASK-610.

## History

- 2026-11-23T10:24:21Z witty-russet-gannet → backlog
- 2026-11-23T10:24:22Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:53Z witty-russet-gannet: changed notes
