---
title: Fix AGENTS.md handling in chitty import backlog-md
status: done
labels:
  - bug,import
created: 2026-10-27
---

## Description

On a clone of sump, chitty init then chitty import backlog-md left AGENTS.md with a stray <!-- BACKLOG.MD GUIDELINES START --> comment and two '## Chitty' sections. init (which import requires) appends the Chitty block; import then replaces only the '## Backlog.md Workflow' section with a second copy, and its pattern stops at the next heading, swallowing the END marker but leaving the START marker.

## Acceptance Criteria

- [x] import removes the whole Backlog.md block, from <!-- BACKLOG.MD GUIDELINES START --> to <!-- BACKLOG.MD GUIDELINES END --> inclusive, and also handles a bare '## Backlog.md Workflow' section with no markers
- [x] After init then import, AGENTS.md contains exactly one Chitty block and no Backlog.md markers
- [x] Running import's AGENTS.md step on a file that has no Backlog.md block changes nothing
- [x] Regression test using sump's real AGENTS.md shape fails before the fix

## Plan

Add filesystem-backed import tests for marker-delimited and bare Backlog.md guide blocks, including an init-shaped AGENTS.md. Replace only the legacy block, preserve unrelated files unchanged, then run make check and verify criteria.

## Notes

Also seen on a clone of circuitry: an opening <CRITICAL_INSTRUCTION> tag inside the Backlog.md block is left behind with the START marker (its closing tag is swallowed). Removing START..END inclusive fixes both. Workaround until fixed: delete those leftover lines by hand.

Ready for review: make check passes.

## Summary

Import now removes complete marker-delimited legacy guide blocks before falling back to bare workflow handling, preventing leftover markers and duplicate Chitty sections. Verified with make check (135 tests).

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
