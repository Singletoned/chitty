---
title: Add a read-only mode that refuses every Chitty write
status: backlog
created: 2026-11-22
---

## Description

Evidence: on 2026-11-21 a cold-reader subagent probing `chitty archive` with no ID ran it in the main checkout and moved 112 done tickets into `chitty/tasks/archive/` before it was killed; it restored them by hand. The cold-read guide already says to report without changing the checkout, but nothing enforces it. Cold readers, reviewers trying a command, dashboards and other tools that only read tickets all want a guarantee instead.

Suggestion: an environment toggle named for its effect, `CHITTY_READ_ONLY=1`. While it is set, every command that would change anything refuses before touching a file, with an error naming the command and the variable, for example `chitty archive refused: CHITTY_READ_ONLY is set`. Reads (`show`, `list`, `next`, `guide`, `path`, `whoami`, `check`, `inbox` without `--pull`) work as usual.

Covered writes:
- Ticket writes through `Repo` (`add`, `edit`, `note`, `archive`, `move`, `renumber`, `fix`): enforce it at the one place every write passes, such as `Repo._prepare_write` in `src/chitty/store.py`, so the CLI and MCP cannot diverge.
- Writes outside the store: `init`, `run` (worktrees, claims, landing), `inbox --pull`, and `suggest`, which writes to another project's inbox.
- The MCP server: its write tools refuse the same way, so an MCP client can be given read-only access.

Then the cold-reader agent definition (`.claude/agents/`) and `chitty guide cold-read` can set or require it. A matching shell allowlist for readers (`chitty show`, `chitty guide`, `git show`, `git log`, `git grep`, plus a scratch `git init` in a temporary directory for trying commands) would cover non-Chitty writes. Tests: one property over every write command, generated from the CLI command list so a new command cannot skip the guard: with the variable set, each refuses and the checkout, Git history and inbox are unchanged.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:32Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:33Z friendly-jade-stoat: changed notes
