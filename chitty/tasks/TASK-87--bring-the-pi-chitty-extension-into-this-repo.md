---
title: Bring the Pi `/chitty` extension into this repo
status: doing
priority: high
created: 2026-11-01
---

## Description

The Pi extension that drives `/chitty work` and `/chitty review` loops lives in `~/.pi/agent/extensions/chitty.ts` (207 lines, with tests), outside version control here. It depends on Chitty's CLI: it parses `chitty list --json`, hard-codes statuses (`todo`, `doing`, `review`), and repeats guide rules in its prompts. So it will break silently with TASK-70, TASK-71 and TASK-74, and it duplicates the work-selection logic planned for `chitty next` (TASK-76). Moving it here (for example `integrations/pi/`) versions it with Chitty and lets `chitty init` install or update it, alongside the Pi session-environment setting (TASK-75). Once `chitty next` exists, the extension keeps only the loop: ask `chitty next --work` or `--review`, prompt, repeat. Equivalents for Claude Code and Codex would sit beside it. Its review-mode prompt must follow whatever review-independence rule is decided (subagent reviews: see the TASK-79 incident, 2026-11-01).

## Acceptance Criteria

- [x] The extension and its tests live in this repo and run in `make check`
- [x] `README.md` documents it
- [x] `chitty init` installs the extension when Pi is installed, and replaces the installed copy only when it differs from the one shipped with Chitty, reporting what it changed; an unchanged install writes nothing
- [x] The installed copy stays correct across Chitty upgrades: a stale install is updated by the upgrade path (TASK-82)

## Plan

Move the shipped Pi extension and its tests into a versioned integration directory; add a testable, idempotent `init` installer that updates only differing copies; update documentation and cover fresh, unchanged, and stale upgrade installs. Run the extension tests and `make check`, then request independent review.

## Notes

Split (2026-11-01): switching the extension to `chitty next` is a follow-up ticket, so this move does not wait for TASK-76. The current copy in `~/.pi` is under that directory's own Git history; the first install replaces it.

Blocked by `TASK-82` review: its stale-install upgrade acceptance criterion relies on the repository upgrade path.

Unblocked (2026-11-01): TASK-82 passed review, so the upgrade path this ticket's stale-install criterion relies on exists.

Moved the Pi extension and node tests into `src/chitty/integrations/pi`; `init` now idempotently installs or refreshes it in an existing Pi agent directory. Verified Python tests, formatter/lint/type checks, and `npm test`.

Review failed: the installer does not support Pi agent directories configured through `PI_CODING_AGENT_DIR`. Pi documents that variable as the agent-directory override, but `pi_settings_path()` always derives `HOME/.pi/agent`; reproduced with an existing custom agent directory and `install_pi_extension()` returned `None`. Resolve the configured agent directory before installing settings or the extension, and add regression coverage.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → doing
