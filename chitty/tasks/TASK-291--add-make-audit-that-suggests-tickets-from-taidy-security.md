---
title: Add `make audit` that suggests tickets from `taidy security`
status: backlog
parent: TASK-290
created: 2026-11-11
---

## Description

- Waits on taidy gaining `taidy security --json` (suggested to taidy 2026-11-11), which runs the scanners and prints findings with `tool`, `rule`, `file`, `line` and `message`.
- Add `scripts/audit.py`, run by a new `make audit` target (`## run security scanners on main; suggest tickets`). For each (tool, rule, file) it sends `chitty suggest . "Audit: <tool> <rule> in <file>"` with the findings' lines and messages. A title already used by a ticket, open or archived, is skipped.
- Exit 0 when it ran; non-zero if taidy fails.

## Acceptance Criteria

- [ ] A test feeds the script recorded `taidy security --json` output with one finding: one suggestion arrives, titled with the tool, rule and file. Running it again sends none. It fails today.

## History

- 2026-11-11T16:18:23Z vivid-yellowhammer → backlog
- 2026-11-11T18:59:32Z vivid-yellowhammer: changed title, description, acceptance criteria
