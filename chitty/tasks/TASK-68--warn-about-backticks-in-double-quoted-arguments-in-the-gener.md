---
title: Warn about backticks in double-quoted arguments in the generated guidance
status: doing
priority: medium
depends_on:
  - TASK-143
created: 2026-11-01
---

## Description

The generated AGENTS.md Chitty section says "Put paths, globs, commands, IDs and code in backticks", which steers agents into the trap below whenever they pass text on the command line in double quotes. Add a line next to it, for example: "Backticks run commands inside double-quoted shell arguments: pass such text in single quotes, or with `--note-file -` and a quoted heredoc (`<<'EOF'`)."

What happened (circuitry, commit 90a902f, task CIRCUIT-67, 2026-10-29): a reviewing agent ran something like

    chitty edit CIRCUIT-67 -s doing --note "Independent review: failed. Acceptance criterion 1 is unmet: `chitty list --all` reports CIRCUIT-68, CIRCUIT-69 and CIRCUIT-71 as `doing`, not `done`. ..."

The generated AGENTS.md guidance tells agents to put commands, IDs and code in backticks, but inside a double-quoted shell argument backticks are command substitution. The shell ran `chitty list --all` and pasted its full output (75 lines, every task CIRCUIT-1 to CIRCUIT-75) into the note, and the other backticked words (`doing`, `done`, a file path) ran as commands and vanished, leaving "reports ... as , not .". The agent noticed and appended a "Correction to the preceding note", but could not remove the broken one, so `chitty show CIRCUIT-67` is 129 lines, 91 of them notes, about 7 KB of which is the dump.

The instruction now lives in `src/chitty/guide.md` and `src/chitty/roles/plan.md`, but `work.md` and `review.md` have none, and workers and reviewers are who hit this. Add this to all four, not just where the instruction is: "Backticks run commands inside double-quoted shell arguments, so pass such text in single quotes. Avoid an apostrophe in the text, or write it as `'\''`." `TASK-143` rewrites `guide.md`, so this follows it. `TASK-67`'s `--note-file` is not built.

## Acceptance Criteria

- [ ] A test shows `chitty guide`, and each role's output, containing the warning, and `__version__` is bumped above `main`'s

## Notes

Suggestion origin: circuitry

Seen again in `docs/pi-token-usage.md` on `pi-token-analysis`, 2026-11-04: about 16 `bash` calls show `command not found` for words such as `chitty_version`, `Repo.finalize` and `todo`, so ticket notes have probably lost text. A worker's note also ran `make check` this way during `TASK-126`. The guidance now also lives in `src/chitty/roles/`, so add the line wherever the backtick instruction is. `TASK-67`'s `--note-file` is not built, so say single quotes only.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the ticket had no criteria, and following the instruction's location would have missed workers and reviewers. Mentioned apostrophes, which single quotes break on.

## History

- 2026-11-01 → backlog
- 2026-11-04T21:41:12Z mellow-newt: changed priority, notes
- 2026-11-04T21:44:40Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T21:44:41Z mellow-newt backlog → todo
- 2026-11-08T11:12:03Z calm-badger todo → doing
