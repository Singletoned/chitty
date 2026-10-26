---
title: Add bash and zsh completion
status: done
labels:
  - cli
created: 2026-10-26
---

## Description

Tab-complete commands, options, task IDs and context names in bash and zsh. Click has completion built in (eval "$(_CHITTY_COMPLETE=zsh_source chitty)"), so this is mostly custom completers for dynamic values plus docs, not a new command.

## Acceptance Criteria

- [x] Commands and options complete in bash and zsh via Click's built-in completion
- [x] ID arguments complete to existing task IDs (non-archived first), and -c to configured context names
- [x] -s completes to the statuses
- [x] Completion outside a chitty repo still completes commands and does not print errors
- [x] Tests cover the dynamic completers
- [x] README shows the one-line setup for bash and zsh

## Plan

Use Click shell completion without adding a command. Attach dynamic shell_complete callbacks to task-ID and context parameters, keeping failures outside a repository empty and silent; Click provides commands/options/status choices. Add direct callback tests and shell setup documentation.

## Notes

Question: Should archived IDs appear? Answer: yes, after active IDs, so users can restore or inspect them while ordinary active-task work stays first.

Verified: Click generates bash/zsh sources; dynamic completion supplies active IDs before archived IDs and configured contexts, returning silently outside a repository. README and PLAN setup/docs updated; make check passes.
