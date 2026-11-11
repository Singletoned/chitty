---
title: Tell cold readers to implement, and planners not to promote on a probe
status: doing
parent: TASK-284
created: 2026-11-11
---

## Description

- Haiku readers often probe instead of implementing, though `chitty guide cold-read` says to implement (TASK-284, from echonomicon).
- In `src/chitty/roles/cold-read.md`: implement the ticket unless probing has already found a problem that will change it; then say so and stop.
- In `src/chitty/roles/plan.md`: a read that only probed does not make a ticket ready; read it again. Only an implementing read whose tests failed first does. Also merge the two bullets there that both start "Cold-read every ticket, even a small one."

## Acceptance Criteria

- [ ] A test in `tests/test_guide_cold_read.py` shows `chitty guide cold-read` saying to implement unless probing found a problem, and `chitty guide plan` saying a probe-only read does not make a ticket ready. It fails today.
- [ ] `chitty guide plan` contains "Cold-read every ticket, even a small one" exactly once.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-298/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T21:10:09Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:20Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:15:01Z vivid-yellow-raven: changed description
- 2026-11-11T21:15:02Z vivid-yellow-raven: changed acceptance criteria, notes
- 2026-11-11T21:15:02Z vivid-yellow-raven cold-read → todo
- 2026-11-11T22:01:25Z mellow-yellow-adder todo → doing
