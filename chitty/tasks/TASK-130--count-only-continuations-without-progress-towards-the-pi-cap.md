---
title: Count only continuations without progress towards the Pi cap
status: todo
labels:
  - bug
priority: high
created: 2026-11-03
---

## Description

`TASK-123` caps continuations at `MAX_CONTINUATIONS` (5) so a stuck agent cannot spend without limit, but it counts every continuation, including productive ones. On 2026-11-03 the `TASK-126` session ended at the cap after 15 minutes, while its agent was ticking a criterion on each turn. Pi shut down with the ticket still `doing`, and `chitty run` reported `todo → doing` as success. A larger ticket therefore cannot finish in one session.

In `src/chitty/integrations/pi/chitty.ts`, count consecutive continuations with no progress, and reset the count on progress. Progress means the output of `chitty show ID --json` differs from the previous check: a tick, note or plan change. Reset on that, not on Git commits, so the measure stays in the ticket and works from any working directory. Keep the value 5, now meaning 5 turns in a row with no ticket change. Add to the work continuation prompt that the agent should carry on to the next criterion without stopping to report.

Decided by the author, cheap to change: there is no overall cap, because criteria are finite and a loop that only writes notes is visible in the ticket and the usage log.

When the cap is reached, the notification says so and names the count. `chitty run` still exits non-zero when status is unchanged, which stops a loop; that is right for a stuck session.

Out of scope: changing `chitty run`, and splitting large tickets.

## Acceptance Criteria

- [ ] Node tests of the decision function show the count resetting when ticket output changes, shutdown after 5 turns in a row without change, and a long run with progress never reaching the cap
- [ ] A Node test shows the work continuation prompt tells the agent to carry on to the next criterion
- [ ] `__version__` is bumped so `chitty init` installs the extension

## History

- 2026-11-03T20:41:13Z lively-panda → todo
