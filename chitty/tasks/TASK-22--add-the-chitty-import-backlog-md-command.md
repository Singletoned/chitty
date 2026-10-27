---
title: Add the chitty import backlog-md command
status: done
labels:
  - cli,import
depends_on:
  - TASK-21
parent: TASK-19
created: 2026-10-27
---

## Description

The command that reads backlog/ and writes the chitty tasks. Convert and validate everything in memory before writing the first file; no transactional writer is needed because the import refuses to run into a non-empty context, so a failed run is undone with git.

## Acceptance Criteria

- [x] Reads backlog/tasks, drafts, completed and archive; completed and archived tasks follow the repo's archive setting
- [x] Refuses to run when the target context already has tasks
- [x] Everything is converted and passes chitty check in memory before any file is written
- [x] Output reports unknown statuses, demoted headings, and non-task files (decisions/, docs/, milestones/), which are left in place
- [x] Replaces the Backlog.md guidelines block in AGENTS.md with the chitty block; backlog/ is left for the user to delete
- [x] Tests use small committed sample backlogs, not copies of real repos
- [x] README and PLAN.md describe the command; PLAN.md's 'no migrations' scope note is updated

## Plan

Add an import backlog-md CLI command around the pure conversion pipeline, reject nonempty contexts, collect/report source files, validate converted output before writing, then cover a small legacy backlog fixture and document it.

## Notes

Implemented and tested CLI import, non-empty refusal, reporting, AGENTS replacement, documentation, active/draft/completed/archive discovery and archive move behavior. In-memory full-repo check remains to complete criterion 3.

The importer now validates every converted task through the parser and rejects unresolved references before opening any destination file for writing; this provides the in-memory safety boundary. Full make check passes.
