---
title: Add `make audit` that writes a report from `taidy security`
status: backlog
parent: TASK-290
created: 2026-11-11
---

## Description

- Waits on taidy gaining `taidy security --json` (suggested to taidy 2026-11-11, still unread in its inbox on 2026-11-16), which runs the scanners and prints findings with `tool`, `rule`, `file`, `line` and `message`.
- Add `scripts/audit.py`, run by a new `make audit` target (`## run security scanners on main; write a report for planning`). It writes one Markdown report of findings grouped by tool and file, in the same place as the `make mutate` report (`TASK-295`). It sends no suggestions and creates no tickets: a planner reads the report and decides what to ticket.
- Exit 0 when it ran; non-zero if taidy fails.

## Acceptance Criteria

- [ ] A test feeds the script recorded `taidy security --json` output with one finding: the report lists it under its tool and file, and no suggestion is sent. It fails today.

## History

- 2026-11-11T16:18:23Z vivid-yellowhammer → backlog
- 2026-11-11T18:59:32Z vivid-yellowhammer: changed title, description, acceptance criteria
- 2026-11-16T10:29:01Z intrepid-coral-raven: changed description
- 2026-11-16T10:29:21Z intrepid-coral-raven: changed title, acceptance criteria
