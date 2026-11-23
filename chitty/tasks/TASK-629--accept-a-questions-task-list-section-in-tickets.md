---
title: Accept a `## Questions` task-list section in tickets
status: backlog
parent: TASK-621
created: 2026-11-23
---

## Description

Allow an optional `## Questions` section in ticket files, placed after Acceptance Criteria. Its body is a flat task list (`- [ ] question` / `- [x] question`), each answered item optionally followed by an indented answer paragraph; decide the exact answer form while planning, keeping it something prettier and mdformat leave unchanged. `chitty check` validates it like Acceptance Criteria and still rejects any other unknown `##` section. `chitty show` prints questions numbered. Round-trip through the pinned formatter tests.

## History

- 2026-11-23T10:40:13Z witty-russet-gannet → backlog
