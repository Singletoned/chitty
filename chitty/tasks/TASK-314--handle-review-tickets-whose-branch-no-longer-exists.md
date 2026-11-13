---
title: Handle review tickets whose branch no longer exists
status: doing
labels:
  - bug
priority: medium
created: 2026-11-13
---

## Description

On 2026-11-09 in `circuitry`, `uv run chitty run --loop --mode review -- --model gpt-6.1-terra` selected `CIRCUIT-67` and stopped with `review ticket CIRCUIT-67 has no branch circuit-67`. A review ticket can outlive its branch after manual branch deletion or cleanup. The review loop should not launch an agent for a missing branch or repeatedly select the same unrecoverable ticket; it should mark the ticket `blocked` with an actionable note naming the missing branch so a person can restore the branch or choose the ticket’s final state.

## Acceptance Criteria

- [ ] A real-Git regression test creates a review ticket, deletes its expected branch, runs review selection, and fails against the current implementation before the fix.
- [ ] When a review ticket’s branch is missing, `chitty run --mode review` moves the ticket to `blocked` with a note naming the ticket and branch, without launching the reviewer.
- [ ] A subsequent review loop does not select the blocked ticket again, and existing review and loop checks pass.

## Notes

Cold read 1 by a fresh Sonnet subagent, `refs/cold-read/TASK-314/1`; the real-Git regression failed before the fix with `Error: review ticket TASK-1 has no branch task-1`, then the focused test passed after the fix. Review and loop suites passed (28 tests). The reader found no serious findings, open decisions, surviving mutants, or missed properties. Starting point to inspect, not trust: `src/chitty/run.py` and `tests/test_review_merge.py` from `git show refs/cold-read/TASK-314/1:<path>`. Full `make check` was blocked in the detached environment by pre-existing missing `mcp`/`mcp_types` imports in pyright.

## History

- 2026-11-13T13:32:42Z lively-violet-puffin → backlog
- 2026-11-13T13:32:50Z lively-violet-puffin backlog → cold-read
- 2026-11-13T13:35:55Z lively-violet-puffin: changed notes
- 2026-11-13T13:35:55Z lively-violet-puffin cold-read → planning
- 2026-11-13T13:35:57Z lively-violet-puffin planning → todo
- 2026-11-13T13:37:56Z quick-pearl-zander todo → doing
