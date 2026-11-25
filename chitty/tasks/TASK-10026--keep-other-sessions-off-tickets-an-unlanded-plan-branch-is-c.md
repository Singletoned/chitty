---
title: Keep other sessions off tickets an unlanded `plan/` branch is changing
status: backlog
labels:
  - bug
created: 2026-11-25
---

## Description

Seen 2026-11-25: a planner on `plan/backlog-2026-11-25` (worktree `.worktrees/plan-backlog-2026-11-25`) rewrote `TASK-676` and committed it there. Meanwhile a triage session (`calm-ochre-quail`) edited `TASK-676` on `main` twice (22:32 and 22:39 to 22:40Z), folding in three more reports, and a renumber on `main` rewrote IDs in its notes. Nothing told either session about the other. The planner's next edit was refused (`planning edit for TASK-676 conflicts with refs/heads/main`), and each landing hit a rename/modify conflict on the ticket file. The planner had to reset its branch, redo its edits and resolve the conflict by hand, twice.

Wanted: when a `plan/` branch is working on a ticket, other sessions (planners and triage on `main` or other `plan/` branches, and `chitty run` selection) can tell, and leave it alone until that branch lands.

Options:

1. Derive the claim from Git (recommended). A ticket that a local `plan/*` branch has changed since it split from `main`, and that branch is not yet merged, is claimed by that branch. `Repo._reject_planning_conflicts` (`src/chitty/store.py`) already walks branch tips for the reverse check. Writes from anywhere else (`edit`, `note`, `archive`, `renumber`) refuse, naming the branch and its worktree; `chitty show` and `chitty list` mark it; `chitty run` does not select it. No new command or state: the planner's first edit (status `planning`) commits on its branch, so the claim exists from then on, and it ends when the branch lands or is deleted. An abandoned branch keeps its claim until the branch cleanup in `AGENTS.md` removes it.
2. An explicit claim recorded on `main` (for example `owner: plan/<name>` set by a `chitty claim` command), released on landing. Visible to every clone, but it adds a command and a commit on `main` per claim, and a crashed planner leaves a stale owner.
3. Warn only, per the `TASK-602` decision to warn generously rather than refuse. Cheapest, but here the other session was an agent that would have to notice and act on a warning.

Related: `TASK-602` (read and write on the current branch, warning about other branches) and `TASK-340` (plan on branches and land them), which this needs to fit.

## History

- 2026-11-25T22:56:40Z golden-coral-stoat → backlog
