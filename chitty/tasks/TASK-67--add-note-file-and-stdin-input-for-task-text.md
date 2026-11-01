---
title: Add `--note-file` and stdin input for task text
status: backlog
created: 2026-11-01
---

## Description

Add `--note-file` (and accept `-` for stdin) to `chitty edit` and `chitty add`, matching the existing `--plan-file` and `--description-file`, so agents can pass text containing backticks without shell quoting. Consider the same for `--summary` and `--ac`.

What happened (circuitry, commit 90a902f, task CIRCUIT-67, 2026-10-29): a reviewing agent ran something like

    chitty edit CIRCUIT-67 -s doing --note "Independent review: failed. Acceptance criterion 1 is unmet: `chitty list --all` reports CIRCUIT-68, CIRCUIT-69 and CIRCUIT-71 as `doing`, not `done`. ..."

The generated AGENTS.md guidance tells agents to put commands, IDs and code in backticks, but inside a double-quoted shell argument backticks are command substitution. The shell ran `chitty list --all` and pasted its full output (75 lines, every task CIRCUIT-1 to CIRCUIT-75) into the note, and the other backticked words (`doing`, `done`, a file path) ran as commands and vanished, leaving "reports ... as , not .". The agent noticed and appended a "Correction to the preceding note", but could not remove the broken one, so `chitty show CIRCUIT-67` is 129 lines, 91 of them notes, about 7 KB of which is the dump.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
