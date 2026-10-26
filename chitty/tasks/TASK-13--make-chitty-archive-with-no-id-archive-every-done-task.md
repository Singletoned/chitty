---
title: Make chitty archive with no ID archive every done task
status: done
labels:
  - cli
created: 2026-10-26
---

## Description

Archiving happens when preparing a merge request, not ticket by ticket. chitty archive with no ID archives every non-archived done task in every context, and reports each one. chitty archive ID still archives a single task.

## Acceptance Criteria

- [x] chitty archive with no ID archives every non-archived done task across all contexts and lists each archived ID
- [x] With no done tasks it says so and exits zero
- [x] chitty archive ID keeps working for a single task
- [x] MCP archive tool supports the same no-ID form
- [x] Autocommit makes one commit for the whole batch
- [x] PLAN.md, README and the agent guide describe archiving at merge-request time

## Plan

Make archive ID optional. Add a repository batch operation that selects non-archived done tasks in every context, moves them before a single finalization/autocommit, and return every archived task for CLI/MCP reporting.

## Notes

Question: What should no-ID JSON return? Answer: a JSON array of archived task objects; it is the natural parallel to the text list and is empty when there is no work.

Verified: archive without ID archives active done tasks from all contexts, returns success with no work, has matching MCP support, and makes one autocommit for the batch. Docs and make check pass.
