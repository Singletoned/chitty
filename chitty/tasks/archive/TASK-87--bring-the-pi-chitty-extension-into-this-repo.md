---
title: Bring the Pi `/chitty` extension into this repo
status: done
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

Resolve Pi agent directories through `PI_CODING_AGENT_DIR` before deriving `settings.json`, preserving the documented `HOME/.pi/agent` fallback. Add isolated regression coverage for extension installation to a custom agent directory; first confirm it fails under the existing implementation, then implement the path resolution and run focused tests plus `make check`.

## Notes

Split (2026-11-01): switching the extension to `chitty next` is a follow-up ticket, so this move does not wait for TASK-76. The current copy in `~/.pi` is under that directory's own Git history; the first install replaces it.

Blocked by `TASK-82` review: its stale-install upgrade acceptance criterion relies on the repository upgrade path.

Unblocked (2026-11-01): TASK-82 passed review, so the upgrade path this ticket's stale-install criterion relies on exists.

Moved the Pi extension and node tests into `src/chitty/integrations/pi`; `init` now idempotently installs or refreshes it in an existing Pi agent directory. Verified Python tests, formatter/lint/type checks, and `npm test`.

Review failed: the installer does not support Pi agent directories configured through `PI_CODING_AGENT_DIR`. Pi documents that variable as the agent-directory override, but `pi_settings_path()` always derives `HOME/.pi/agent`; reproduced with an existing custom agent directory and `install_pi_extension()` returned `None`. Resolve the configured agent directory before installing settings or the extension, and add regression coverage.

Resolved the review finding: `PI_CODING_AGENT_DIR` now selects the Pi agent directory for both settings and extension installation. Added a regression test that failed before the fix. Verified with `uv run python -m unittest tests.test_actor tests.test_pi_extension` and `make check`.

Reviewed: independent fix `f0d98ea` resolves the documented `PI_CODING_AGENT_DIR` override before both settings and extension paths, with regression coverage for installing into a custom agent directory. Verified the focused regression and `make check`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
- 2026-11-05T14:44:49Z vivid-wren done → archived
