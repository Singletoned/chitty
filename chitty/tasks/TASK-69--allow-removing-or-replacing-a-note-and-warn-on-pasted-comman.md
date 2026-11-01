---
title: Allow removing or replacing a note, and warn on pasted command output
status: backlog
created: 2026-11-01
---

## Description

Add a way to remove or replace a note, for example `chitty edit ID --rm-note N` (numbered as `chitty show` prints them) or `--replace-note N TEXT`. Notes are append-only through the CLI and hand-editing task files is forbidden, so a broken note is permanent. Keeping the removal in History would preserve the audit trail. Separately, `chitty edit`/`chitty fix` could warn when a note looks like pasted command output: many lines, or lines starting with task IDs and statuses.

What happened (circuitry, commit 90a902f, task CIRCUIT-67, 2026-10-29): a reviewing agent ran something like

    chitty edit CIRCUIT-67 -s doing --note "Independent review: failed. Acceptance criterion 1 is unmet: `chitty list --all` reports CIRCUIT-68, CIRCUIT-69 and CIRCUIT-71 as `doing`, not `done`. ..."

The generated AGENTS.md guidance tells agents to put commands, IDs and code in backticks, but inside a double-quoted shell argument backticks are command substitution. The shell ran `chitty list --all` and pasted its full output (75 lines, every task CIRCUIT-1 to CIRCUIT-75) into the note, and the other backticked words (`doing`, `done`, a file path) ran as commands and vanished, leaving "reports ... as , not .". The agent noticed and appended a "Correction to the preceding note", but could not remove the broken one, so `chitty show CIRCUIT-67` is 129 lines, 91 of them notes, about 7 KB of which is the dump.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
