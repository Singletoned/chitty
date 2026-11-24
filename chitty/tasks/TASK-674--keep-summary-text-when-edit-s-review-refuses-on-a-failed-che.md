---
title: Keep --summary text when edit -s review refuses on a failed check
status: backlog
created: 2026-11-24
---

## Description

When `chitty edit <ID> -s review --summary-file F` refuses because the configured check fails, the whole edit is discarded, summary included, and the error does not say so. Seen 2026-11-23 on TASK-643..646: the check failed only because the worktrees were made by hand with `git worktree add` and the configured `setup` (`make install`) had not run. pyright could not resolve the `mcp` extra. Rerunning setup fixed the check, but each summary had to be rewritten from scratch.

Suggested fixes, either one:
1. Apply the non-status fields (summary, notes) and refuse only the status change, saying so.
2. At least say "summary not saved" in the refusal.

Related: when the check fails in a worktree whose environment was never set up (for example no `.venv`, or imports missing), it could point out that the configured `setup` may not have run there.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:37Z zesty-coral-newt → backlog
- 2026-11-24T22:21:38Z zesty-coral-newt: changed notes
