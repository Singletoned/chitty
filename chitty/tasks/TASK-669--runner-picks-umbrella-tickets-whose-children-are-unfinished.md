---
title: Runner picks umbrella tickets whose children are unfinished
status: backlog
created: 2026-11-24
---

## Description

In shelfpath, TASK-5 is a parent of TASK-6 to TASK-9 and only does end-to-end verification once they are done. When it was moved to todo on 2026-11-23, `chitty run --loop --mode work` picked it within 15 minutes (actor intrepid-yellow-zander) and the worker blocked it again 16 seconds later because its children were unfinished. That was a wasted run and noise in the blocked list. Suggest that `chitty next` / `chitty run` skip a ticket while any of its children are not done, as it presumably already does for unmet `depends_on`. Also seen again: run locks (`.git/chitty/run/TASK-*.lock`) were left behind after the workers exited (PIDs 33747, 6519, 28502 dead).

## Notes

Suggestion origin: shelfpath

## History

- 2026-11-24T22:21:32Z zesty-coral-newt → backlog
- 2026-11-24T22:21:33Z zesty-coral-newt: changed notes
