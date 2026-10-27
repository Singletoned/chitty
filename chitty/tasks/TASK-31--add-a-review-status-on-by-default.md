---
title: Add a review status, on by default
status: todo
labels:
  - cli,config
depends_on:
  - TASK-30
created: 2026-10-27
---

## Description

Completed work is reviewed by a different agent or a human before it is done, and well before merge-request time. Status order becomes backlog → todo → doing → blocked → review → done. A repo setting turns enforcement on or off.

## Acceptance Criteria

- [ ] review is a status between blocked and done in every context; plain list shows it; completion includes it
- [ ] Repo setting review = true | false; init writes review = true for new repos and adds it on upgrade; any other value is a config error
- [ ] With review = true, doing → done (and any non-review → done) is refused with a message to set -s review; with review = false, review is optional
- [ ] Nothing else is required to enter review (checklist state is not checked)
- [ ] review → doing requires a --note in the same command (CLI and MCP), like blocked
- [ ] Agent guide: set -s review when you think it is ready; never review a ticket you worked on; pass with -s done and a Reviewed: note; fail with -s doing and a note; out-of-scope findings become new tickets; review promptly, not at merge-request time
- [ ] Tests, PLAN.md, README and AGENTS.md updated
