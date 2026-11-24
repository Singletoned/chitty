---
title: Tolerate a branch deleted while Chitty scans branches
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

On 2026-11-23, `chitty edit TASK-576 ...` run in `.worktrees/task-576` failed with:

    Error: `git ls-tree -r -z --full-tree refs/heads/task-yj6vbs -- chitty` failed in .worktrees/task-576:
    fatal: Not a valid object name refs/heads/task-yj6vbs

Another session had deleted branch `task-yj6vbs` between Chitty listing branches and reading them. Re-running the same command succeeded. With many runners landing and cleaning up branches in one checkout, this race will recur. Fix: when reading a branch that was listed but no longer resolves, skip that branch (it is gone, so it holds no newer ticket version) instead of failing the whole command. Test: list branches, delete one before the read (inject between the two steps), and check the command still succeeds.

## Notes

Suggestion origin: chitty

Duplicate of TASK-233 (a branch deleted during ticket discovery crashes the command); the evidence is recorded there.

Triage 2026-11-24: not archived, because its target ticket has a branch with a held run lock; fold this into the target when planning it, then archive.

## History

- 2026-11-24T22:21:34Z zesty-coral-newt → backlog
- 2026-11-24T22:21:35Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:13Z zesty-coral-newt: changed labels, notes
- 2026-11-24T22:41:02Z zesty-coral-newt: changed notes
