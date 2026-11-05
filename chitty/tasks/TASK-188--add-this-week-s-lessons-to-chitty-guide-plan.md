---
title: Add this week's lessons to `chitty guide plan`
status: doing
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`src/chitty/roles/plan.md` tells agents in every repository how to write tickets and cold-read them, but not what the cold reads here have since taught. Add these four bullets, close to this wording, after the existing cold-read bullet, keeping the file to about 35 lines, and removing from the existing cold-read bullet whatever the third new bullet repeats:

- "Ask of each criterion: could it pass with nothing built? If so, name the case that fails today, and have the worker record that the test failed first."
- "A worker cannot verify a criterion needing a real `chitty run` or agent session, and must not start one. Give that check to a person: a separate `-c human` ticket that depends on this one."
- "Give the cold reader the ticket ID, the code most at risk and what you doubt. Ask it to try behaviour where it can rather than assume it, and to report each finding with file, line, why it matters and the exact wording to change."
- "Re-check claims about other tickets just before promoting, because they can land during the read."

Each comes from 2026-11-05: `TASK-178` and `TASK-184` had criteria that could pass with nothing built, `TASK-142`'s real-session criterion led a worker to change `main`'s setup, and `TASK-181` described work as still to come that merged during its read. `TASK-181` also edits `plan.md`, on another bullet.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py` shows `guide("plan")` containing `nothing built`, `must not start one`, `rather than assume` and `just before promoting`

## Plan

Update src/chitty/roles/plan.md with the four requested cold-read lessons immediately after the existing cold-read bullet, removing any repeated guidance from that bullet. Add or adjust the TestGuide test in tests/test_cli.py so guide('plan') asserts all four lesson phrases, then run the focused test and make check.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: how `human` tickets work, the line count, and overlap with the existing bullet. Removed the version bump, because `plan.md` does not reach `AGENTS.md`, which also avoids a conflict. It checked the facts cited about the other tickets against their notes.

## History

- 2026-11-05T14:13:56Z mellow-newt → backlog
- 2026-11-05T14:23:19Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:23:20Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:23:21Z mellow-newt backlog → todo
- 2026-11-05T23:40:54Z vivid-wren todo → doing
- 2026-11-05T23:41:08Z vivid-wren: wrote the plan
