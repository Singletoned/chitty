---
title: "Cold-read guide: report reds in the reply, keep scratch in the worktree, filter findings"
status: backlog
created: 2026-11-10
---

## Description

Three additions to the cold-read guide, `src/chitty/roles/cold-read.md`, from planning mullion. Each saves the planner a round of fixes or a repeat read.

- Readers may not write to Chitty, so tickets that ask the worker to record a failing test in a note confused them. Tell readers to put red test output in their report, never in a ticket note.
- Readers wrote scratch logs to `/tmp` or the main checkout. Tell them to keep every scratch file inside the read worktree and delete it before running the check, because the check may lint stray files.
- Reads converged only once readers reported just the findings that change what a worker builds or how a reviewer verifies it, and listed choices left to the worker in one line without asking for a ticket change. Say that in the report section.

Keep each addition to one or two lines. Put tests in a new `tests/test_guide_cold_read_reports.py` in the style of `tests/test_guide_plan.py` (assert phrases in the whitespace-normalised `guide("cold-read")` text).

## Acceptance Criteria

- [ ] `guide("cold-read")` tells readers to put failing test output in their report, not in a ticket note.
- [ ] `guide("cold-read")` tells readers to keep scratch files inside the read worktree and delete them before running the check.
- [ ] `guide("cold-read")` tells readers to report only findings that change what a worker builds or how a reviewer verifies it, and to list worker choices in one line.

## History

- 2026-11-10T14:08:40Z jolly-heron → backlog
