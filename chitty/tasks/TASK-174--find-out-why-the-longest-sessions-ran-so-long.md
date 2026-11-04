---
title: Find out why the longest sessions ran so long
status: backlog
priority: medium
owner: human
depends_on:
  - TASK-170
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 2. 7 sessions of 100 or more calls, as at 2026-11-04 and named by `scripts/pi_calls.py`, take 37% of spend, against a median session of $0.35, and 42% of spend is at 60-100k tokens of context. The doc says to investigate this before changing anything. This is for the planning session, not a worker: read those sessions, using the scripts, and say what kept each going, such as ticket size, repeated failures or a stuck tool. Owner `human` is how `chitty next` skips it. Earlier compaction is not an obvious answer, because re-reading may cancel the saving.

## Acceptance Criteria

- [ ] A note says why each of the 7 ran long, and proposes at most three changes, or says none is worthwhile

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: which sessions, since the sample was still growing.

## History

- 2026-11-04T21:41:09Z mellow-newt → backlog
- 2026-11-04T21:44:30Z mellow-newt: changed description, notes
