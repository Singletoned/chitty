---
title: Count only continuations without progress towards the Pi cap
status: done
labels:
  - bug
priority: high
depends_on:
  - TASK-129
created: 2026-11-03
---

## Description

`TASK-123` caps continuations at `MAX_CONTINUATIONS` (5) so a stuck agent cannot spend without limit, but it counts every continuation, including productive ones. On 2026-11-03 the `TASK-126` session ended at the cap after 15 minutes, while its agent was ticking a criterion on each turn. Pi shut down with the ticket still `doing`, and `chitty run` reported `todo → doing` as success. A larger ticket therefore cannot finish in one session.

In `src/chitty/integrations/pi/chitty.ts`, count consecutive continuations with no progress, and reset the count on progress. Progress means the output of `chitty show ID --json` differs from the previous check: a tick, note or plan change. Reset on that, not on Git commits, so the measure stays in the ticket. Take the baseline in `start()`. Keep a hash of the output in the persisted state, to keep session entries small, and validate it in `latestState`, so a resumed session keeps its count. Both modes use the same rule: a reviewer that ends five turns without a verdict is equally stuck. Keep the value 5, now meaning 5 turns in a row with no ticket change. Add to the work continuation prompt that the agent should carry on to the next criterion without stopping to report.

Decided by the author, cheap to change: there is no overall cap, because criteria are finite and a loop that only writes notes is visible in the ticket and the usage log.

If `chitty show` fails, notify and shut down, leaving the count alone. Today it throws out of `agent_settled`, leaving Pi idle, which would hang an unattended loop.

When the cap is reached, the notification says so and names the count. `chitty run` still exits non-zero when status is unchanged, which stops a loop; that is right for a stuck session.

Rollout: after `TASK-129`, landing does not install the extension by itself; `chitty init` in the main checkout does, which `TASK-120` automates. If `main` already has this version when the ticket is ready for review, bump again: identical bumps merge silently, and repositories would then never learn about the later change. Rebase on `TASK-126`, which rewrites much of the same file.

Out of scope: changing `chitty run`, and splitting large tickets.

## Acceptance Criteria

- [x] Node tests of the decision function show the count resetting when ticket output changes, shutdown after 5 turns in a row without change, and a long run with progress never reaching the cap
- [x] A Node test shows the work continuation prompt tells the agent to carry on to the next criterion
- [x] Node tests cover the baseline taken at start, a resumed session keeping its count, the notification naming the count, both modes using the rule, and a failing `chitty show` notifying and shutting down
- [x] `__version__` is bumped above `main`'s

## Plan

1. Read the JSON ticket state at start and after each settled turn, storing its compact hash with the consecutive no-progress count. 2. Make the decision function advance or reset that count and return an actionable reason, including the count at the cap. 3. Shut down cleanly with a notification when reading the ticket fails. 4. Add focused Node tests for change detection, persistence, modes, prompt, failure, and the version bump; run the required checks.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03, with `TASK-129`. Fixed: criterion 3 wrongly said the bump makes `chitty init` install the extension, when `init` always checks the file itself; the baseline; persisted state; review mode; `show` failing; and the rollout and bump. It also confirmed `show --json` is stable at rest. Rejected: a tick then untick never reaching the cap, and notes counting as progress, because both are visible in the ticket and the usage log, and this guards against a stuck agent, not a hostile one. Testing that real `show` output changes on each edit, because every changing write appends to History by design. `show` reading a newer copy from another branch, because the guard from `TASK-105` stops a worker's ticket being edited elsewhere. How to pass the values to the decision function, which is the worker's choice.

Landing moved from `TASK-120` to `TASK-131`, so read references to that step accordingly.

Order changed with the human, 2026-11-03: this now lands before `TASK-126`, which waits for it, because `TASK-126` could otherwise hit the cap again. Ignore the line about rebasing on `TASK-126`; that ticket rebases on this one instead.

Implementation choice: use a deterministic hash of the complete `chitty show ID --json` output as the progress baseline. This directly matches the specified comparison while keeping session entries small; changing hash algorithm later is cheap because only within-session equality matters. The implementation will document this default beside the state field.

Cold-read delegation was attempted before implementation, but the available `explorer` subagent could not start because its configured Anthropic credential is absent, then remained locked as processing. I will cover the same scope with focused code and test inspection; a separate agent will perform the required final review.

Verified all criteria: `npm test` passed all 20 Pi integration tests (including progression, cap, baseline/resume, both modes, prompt, and failed-show shutdown); `make check` passed ruff, pyright, and 215 Python tests; `__version__` is `0.1.23`, above `main` at `0.1.22`.

Reviewed: all four criteria verified independently; npm test (20 pass) and make check pass.

## History

- 2026-11-03T20:41:13Z lively-panda → todo
- 2026-11-03T20:44:53Z lively-panda: changed dependencies, description, acceptance criteria, notes
- 2026-11-03T20:46:22Z lively-panda: changed notes
- 2026-11-03T21:00:46Z lively-panda: changed dependencies, notes
- 2026-11-03T21:20:49Z kind-marten: changed notes; wrote the plan
- 2026-11-03T21:20:49Z kind-marten todo → doing
- 2026-11-04T08:18:27Z kind-marten: changed notes; ticked acceptance criteria
- 2026-11-04T08:18:38Z kind-marten doing → review
- 2026-11-04T08:22:34Z amber-heron: changed notes
- 2026-11-04T08:22:34Z amber-heron review → done
