---
title: Fix AGENTS.md handling in chitty import backlog-md
status: todo
labels:
  - bug,import
created: 2026-10-27
---

## Description

On a clone of sump, chitty init then chitty import backlog-md left AGENTS.md with a stray <!-- BACKLOG.MD GUIDELINES START --> comment and two '## Chitty' sections. init (which import requires) appends the Chitty block; import then replaces only the '## Backlog.md Workflow' section with a second copy, and its pattern stops at the next heading, swallowing the END marker but leaving the START marker.

## Acceptance Criteria

- [ ] import removes the whole Backlog.md block, from <!-- BACKLOG.MD GUIDELINES START --> to <!-- BACKLOG.MD GUIDELINES END --> inclusive, and also handles a bare '## Backlog.md Workflow' section with no markers
- [ ] After init then import, AGENTS.md contains exactly one Chitty block and no Backlog.md markers
- [ ] Running import's AGENTS.md step on a file that has no Backlog.md block changes nothing
- [ ] Regression test using sump's real AGENTS.md shape fails before the fix

## History

- 2026-10-27 → todo
