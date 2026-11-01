---
title: Bring the Pi `/chitty` extension into this repo
status: blocked
priority: high
created: 2026-11-01
---

## Description

The Pi extension that drives `/chitty work` and `/chitty review` loops lives in `~/.pi/agent/extensions/chitty.ts` (207 lines, with tests), outside version control here. It depends on Chitty's CLI: it parses `chitty list --json`, hard-codes statuses (`todo`, `doing`, `review`), and repeats guide rules in its prompts. So it will break silently with TASK-70, TASK-71 and TASK-74, and it duplicates the work-selection logic planned for `chitty next` (TASK-76). Moving it here (for example `integrations/pi/`) versions it with Chitty and lets `chitty init` install or update it, alongside the Pi session-environment setting (TASK-75). Once `chitty next` exists, the extension keeps only the loop: ask `chitty next --work` or `--review`, prompt, repeat. Equivalents for Claude Code and Codex would sit beside it. Its review-mode prompt must follow whatever review-independence rule is decided (subagent reviews: see the TASK-79 incident, 2026-11-01).

## Acceptance Criteria

- [ ] The extension and its tests live in this repo and run in `make check`
- [ ] `README.md` documents it
- [ ] `chitty init` installs the extension when Pi is installed, and replaces the installed copy only when it differs from the one shipped with Chitty, reporting what it changed; an unchanged install writes nothing
- [ ] The installed copy stays correct across Chitty upgrades: a stale install is updated by the upgrade path (TASK-82)

## Notes

Split (2026-11-01): switching the extension to `chitty next` is a follow-up ticket, so this move does not wait for TASK-76. The current copy in `~/.pi` is under that directory's own Git history; the first install replaces it.

Blocked by `TASK-82` review: its stale-install upgrade acceptance criterion relies on the repository upgrade path.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
