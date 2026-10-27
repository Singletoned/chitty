---
title: Add chitty suggest to send a task to another project's inbox
status: done
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

- [x] PROJECT is a registered name, or a path to a repo whose config names its project
- [x] An unknown name is an error listing the known names and saying to use --create if the project doesn't use chitty yet
- [x] --create registers a recipient with no repo and delivers the suggestion; later suggestions to that name need no flag
- [x] -d is optional; every suggestion records its origin: source repo (if any), the task being worked on (if given), and the date
- [x] Writes are atomic (write to a temp name, then rename) so pull never sees half a file
- [x] MCP suggest tool with the same rules
- [x] Shell completion offers registered names
- [x] Tests, PLAN.md, README and the agent guide (when and how to suggest) updated

## Plan

Implement atomic machine-inbox suggestion writing plus registered-name/path resolution, expose CLI and MCP parity, then add isolated-XDG tests and docs.

## Notes

Implemented atomic suggest delivery with registered-name/path/create resolution, origin/task/date metadata, CLI/MCP parity and shell completion; added inbox tests and documentation. Full make check passes.
