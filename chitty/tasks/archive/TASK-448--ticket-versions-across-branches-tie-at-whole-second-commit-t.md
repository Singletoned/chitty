---
title: Ticket versions across branches tie at whole-second commit time
status: backlog
created: 2026-11-19
---

## Description

Supersedes the earlier suggestion "Fix flaky test_run_cases repair step": that test is fixed in c22e3a6. Root cause: `git.historical_files` (`src/chitty/git.py`, via `_latest_changes`) picks the newest version of each ticket across branches by `%ct`, which has one-second resolution. When two diverged branches change a ticket in the same second, the first commit that `git log --topo-order` lists wins, which is arbitrary. On Linux CI the tests run fast enough that `chitty run` recording `error` on main and the fake agent committing on the ticket branch landed in one second, so main won and `test_run_cases` failed on every Linux run (v0.4.0 and v0.4.1 release runs). Changing the tie-break to "current branch wins" is not a fix: `test_run_cases` (line ~1802) and `test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review` expect main's same-second `error` to win over the branch claim, so neither tie-break rule is correct; the information is missing. The fix in c22e3a6 dates the fake agent commit one second later, as a real agent's always is. Real agents are very unlikely to tie, but `chitty run` itself makes several commits per second across main and branches. A durable fix needs an ordering that does not depend on wall-clock seconds, for example comparing History entry timestamps with sub-second precision or a monotonic counter. Decide whether it is worth doing.

## Notes

Suggestion origin: chitty

Archived as covered by the ticket-state work: `TASK-367`, `TASK-378`, `TASK-386`.

## History

- 2026-11-19T20:55:22Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:23Z sunny-white-dormouse: changed notes
- 2026-11-19T20:56:47Z sunny-white-dormouse: changed notes
- 2026-11-19T20:56:50Z sunny-white-dormouse backlog → archived
