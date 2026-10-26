---
title: Recognise a Summary section
status: done
labels:
  - format
priority: medium
created: 2026-10-26
---

## Description

Backlog.md tasks end with a Final Summary: what changed, why, how it was verified, and follow-ups. It's the handoff a later reader needs, and 59 of circuitry's 66 tasks have one. Chitty only recognises Description, Acceptance Criteria, Plan and Notes, and rejects any other ## heading. Recognise ## Summary as a fifth section, written when a task is finished, and have chitty edit set it the way it sets the Plan.

## Acceptance Criteria

- [x] ## Summary is a recognised section, placed after Notes
- [x] chitty edit --summary TEXT sets or replaces it; the MCP edit tool supports the same
- [x] The agent guide tells agents to write a summary when setting -s done
- [x] PLAN.md and the README describe the section

## Plan

Add Summary to the model section order and expose a matching CLI/MCP edit field, then update guide/docs and parser/round-trip coverage.

## Notes

Verified Summary parses and renders after Notes, is editable through CLI/MCP, and full make check passes.
