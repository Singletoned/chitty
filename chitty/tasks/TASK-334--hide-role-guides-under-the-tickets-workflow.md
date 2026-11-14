---
title: Hide role guides under the tickets workflow
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-330
created: 2026-11-14
---

## Description

Under `workflow = "tickets"`, hide the role guides.

- `chitty guide` with no role still prints the managed block.
- The roles `work`, `review`, `repair`, `cold-read`, `setup` and `plan` are not offered: `chitty guide --help` shows only the plain `chitty guide` example, and asking for one of them fails, exit 1, saying it needs `workflow = "runner"` in the config.
- Outside a Chitty repository, and under `workflow = "runner"`, behaviour is unchanged.

## Acceptance Criteria

- [ ] Under `tickets`, `chitty guide` prints the managed block and `chitty guide --help` shows no role examples.
- [ ] Under `tickets`, `chitty guide <role>` for `work`, `review`, `repair`, `cold-read`, `setup` or `plan` exits 1 with a message naming `workflow = "runner"`.
- [ ] Outside a Chitty repository and under `runner`, `chitty guide` and its help are unchanged.
- [ ] Tests in `tests/test_guide_workflow.py` cover criteria 1 to 3, and fail without the change.

## History

- 2026-11-14T18:21:59Z friendly-ginger-adder → planning
- 2026-11-14T18:23:32Z friendly-ginger-adder: changed dependencies
