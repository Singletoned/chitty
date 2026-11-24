---
title: Runner picks umbrella tickets whose children are unfinished
status: backlog
created: 2026-11-24
---

## Description

In shelfpath, TASK-5 is a parent of TASK-6 to TASK-9 and only does end-to-end verification once they are done. When it was moved to todo on 2026-11-23, `chitty run --loop --mode work` picked it within 15 minutes (actor intrepid-yellow-zander) and the worker blocked it again 16 seconds later because its children were unfinished. That was a wasted run and noise in the blocked list. Suggest that `chitty next` / `chitty run` skip a ticket while any of its children are not done, as it presumably already does for unmet `depends_on`. Also seen again: run locks (`.git/chitty/run/TASK-*.lock`) were left behind after the workers exited (PIDs 33747, 6519, 28502 dead).

## Notes

Suggestion origin: shelfpath

Triage 2026-11-24: needs a decision from the person before planning. Option A: `chitty next` and `chitty run` skip a ticket while any of its children is not `done`; this changes the selection rule for every repository (`needs-minor`), and a parent that has its own work to do first would then need its children re-parented. Option B: no code change; the plan guide says a parent that only verifies its children gets `depends_on` on each child, which selection already honours. The stale run locks in the description are covered by TASK-682.

Decided with the person, 2026-11-24: no change. `depends_on` already keeps a ticket out of selection until its dependencies are `done`; `parent` only groups tickets. A parent that should wait for its children gets `depends_on` on each of them (shelfpath TASK-5 had only `parent`). The stale run locks mentioned here are covered by TASK-682. Archived.

## History

- 2026-11-24T22:21:32Z zesty-coral-newt → backlog
- 2026-11-24T22:21:33Z zesty-coral-newt: changed notes
- 2026-11-24T23:10:58Z zesty-coral-newt: changed notes
- 2026-11-24T23:20:35Z zesty-coral-newt: changed notes
- 2026-11-24T23:20:38Z zesty-coral-newt backlog → archived
