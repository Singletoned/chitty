---
title: Add bash and zsh completion
status: todo
labels:
  - cli
created: 2026-10-26
---

## Description

Tab-complete commands, options, task IDs and context names in bash and zsh. Click has completion built in (eval "$(_CHITTY_COMPLETE=zsh_source chitty)"), so this is mostly custom completers for dynamic values plus docs, not a new command.

## Acceptance Criteria

- [ ] Commands and options complete in bash and zsh via Click's built-in completion
- [ ] ID arguments complete to existing task IDs (non-archived first), and -c to configured context names
- [ ] -s completes to the statuses
- [ ] Completion outside a chitty repo still completes commands and does not print errors
- [ ] Tests cover the dynamic completers
- [ ] README shows the one-line setup for bash and zsh
