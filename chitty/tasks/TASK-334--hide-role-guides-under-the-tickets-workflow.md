---
title: Hide role guides under the tickets workflow
status: cold-read
labels:
  - needs-minor
owner: friendly-ginger-adder
depends_on:
  - TASK-330
  - TASK-332
created: 2026-11-14
---

## Description

Under `workflow = "tickets"` (the resolved `config.workflow` from TASK-330), hide the role guides.

- `chitty guide` with no role still prints the managed block (TASK-332 decides its text).
- Every role in `ROLE_NAMES` (`work`, `review`, `repair`, `plan`, `cold-read`, `setup`) is unavailable: `chitty guide <role> [ID]` exits 1 with `chitty guide <role> needs workflow = "runner" in the Chitty config`, and `chitty guide --help` shows only the plain `chitty guide` example, with no role examples or the line about which roles take an ID.
- Put the refusal in `guide()` in `src/chitty/store.py`, which gains the workflow as a parameter, so every caller decides; `src/chitty/run.py` passes its repository's workflow.
- When no config is found, or it fails to load, behave as `runner`, as today.
- No property test: a small fixed set (six roles, two workflows, no repository), each case tested. Tests go in `tests/test_guide_workflow.py`.

## Acceptance Criteria

- [ ] In a temp repository with `workflow = "tickets"`, for each of the six roles, `chitty guide <role>` exits 1 with the message naming the role and `workflow = "runner"`, and prints nothing on stdout. Fails today.
- [ ] Under `tickets`, `chitty guide` exits 0 and prints the managed block, and `chitty guide --help` mentions no role name.
- [ ] Under `runner`, and outside a repository, each role guide and `chitty guide --help` give the same output as before (compare with the output at the commit before this change). `make check` passes.

## History

- 2026-11-14T18:21:59Z friendly-ginger-adder → planning
- 2026-11-14T18:23:32Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:29:50Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:30:01Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:56:14Z friendly-ginger-adder: changed owner
- 2026-11-14T18:56:14Z friendly-ginger-adder planning → cold-read
