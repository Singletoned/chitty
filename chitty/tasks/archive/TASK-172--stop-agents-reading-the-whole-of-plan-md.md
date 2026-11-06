---
title: Stop agents reading the whole of `PLAN.md`
status: done
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 6. `PLAN.md` is the most expensive file agents read, at about $3 over the sample, because `AGENTS.md` line 3 tells them to read it before changing behaviour. It is 671 lines in 21 sections. Change that line to say: find the relevant section with `grep -n '^## ' PLAN.md` and read only that, and update it when a decision changes. Keep `PLAN.md` as one file. This line is outside the managed block, so `chitty init` does not touch it, and no version bump is needed.

## Acceptance Criteria

- [x] `AGENTS.md` says to read only the relevant section of `PLAN.md`, and says how to find it

## Plan

Update the repository's AGENTS.md instruction to direct agents to locate the relevant PLAN.md section with grep -n '^## ' PLAN.md and read only that section. Verify the wording and run the repository checks.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. No faults. Raised to high, because the doc says to do this and `TASK-171` first. `AGENTS.md` line 16 and `README.md` line 10 mention `PLAN.md` without telling agents to read it, so they stay.

Reviewed: criterion 1 is met; AGENTS.md directs agents to locate headings with grep -n '^## ' PLAN.md and read only the relevant section. make check passed (268 unittest tests, ruff, pyright); npm test passed.

## Summary

Updated AGENTS.md to locate PLAN.md headings with grep and read only the relevant section. Verified criterion 1, ran chitty fix, make check, and npm test; all checks passed.

## History

- 2026-11-04T21:41:07Z mellow-newt → backlog
- 2026-11-04T21:44:25Z mellow-newt: changed priority, description, notes
- 2026-11-04T21:44:26Z mellow-newt backlog → todo
- 2026-11-05T20:36:25Z calm-otter todo → doing
- 2026-11-05T20:36:37Z calm-otter: wrote the plan
- 2026-11-05T20:41:52Z calm-otter: ticked acceptance criteria
- 2026-11-05T20:42:04Z calm-otter: changed summary
- 2026-11-05T20:42:04Z calm-otter doing → review
- 2026-11-05T20:47:36Z honest-stoat: changed notes
- 2026-11-05T20:47:36Z honest-stoat review → done
- 2026-11-06T16:46:09Z jolly-quail done → archived
