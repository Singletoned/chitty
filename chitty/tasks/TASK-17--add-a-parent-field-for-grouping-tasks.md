---
title: Add a parent field for grouping tasks
status: doing
labels:
  - format
priority: medium
created: 2026-10-26
---

## Description

Backlog.md expresses subtasks as IDs like TASK-33.7. Chitty deliberately has no subtask IDs, but repos still group work under one goal: circuitry has 25 subtasks across 6 parents. Add an optional parent frontmatter field holding a full ID in the same repo, so subtasks keep flat IDs and still point at their parent. chitty list and show should make the grouping visible, and the Backlog.md importer will use the field.

## Acceptance Criteria

- [ ] Optional parent frontmatter field holding a full PREFIX-n ID; shorthand is expanded before writing, as with depends_on
- [ ] chitty add and chitty edit can set and clear parent
- [ ] chitty check reports a parent that doesn't exist, a task that is its own parent and parent cycles; chitty fix repairs only the safe cases
- [ ] chitty move rewrites parent references, and archive or delete handles parents with children the same way as depends_on
- [ ] chitty show lists a task's children; chitty list can filter by parent
- [ ] PLAN.md, the README and the agent guide describe the field

## Plan

Extend the task model and store with a canonical optional parent ID, mirror parent validation and safe repair alongside dependencies, and apply reference rewrites on move/delete. Then expose it through CLI/MCP add/edit/list/show, document it, and add focused regression coverage before the full check.
