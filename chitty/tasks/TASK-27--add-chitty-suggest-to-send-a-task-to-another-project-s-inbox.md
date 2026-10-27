---
title: Add chitty suggest to send a task to another project's inbox
status: doing
labels:
  - cli
depends_on:
  - TASK-26
parent: TASK-25
created: 2026-10-27
---

## Description

chitty suggest PROJECT TITLE [-d TEXT] writes one suggestion file into PROJECT's inbox. Works from any directory, including outside a chitty repo.

## Acceptance Criteria

- [ ] PROJECT is a registered name, or a path to a repo whose config names its project
- [ ] An unknown name is an error listing the known names and saying to use --create if the project doesn't use chitty yet
- [ ] --create registers a recipient with no repo and delivers the suggestion; later suggestions to that name need no flag
- [ ] -d is optional; every suggestion records its origin: source repo (if any), the task being worked on (if given), and the date
- [ ] Writes are atomic (write to a temp name, then rename) so pull never sees half a file
- [ ] MCP suggest tool with the same rules
- [ ] Shell completion offers registered names
- [ ] Tests, PLAN.md, README and the agent guide (when and how to suggest) updated

## Plan

Implement atomic machine-inbox suggestion writing plus registered-name/path resolution, expose CLI and MCP parity, then add isolated-XDG tests and docs.
