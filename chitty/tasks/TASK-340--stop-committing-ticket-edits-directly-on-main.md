---
title: Stop committing ticket edits directly on main
status: planning
depends_on:
  - TASK-602
created: 2026-11-16
---

## Description

Planning sessions and the runner commit ticket edits in the main checkout while other agents do the same, which is why amending or rewriting `main` history is unsafe and why concurrent sessions race. The learned rule in `AGENTS.md` already forbids implementation and doc fixes on `main`; ticket edits are the remaining exception.

Direction from the person, 2026-11-22: plan on a branch, and squash its commits before merging it into `main`. On 2026-11-22, 755 of the 824 commits on `main` in 24 hours were Chitty bookkeeping, about 20 to 30 per ticket; cold-read rounds alone make about 10 per ticket while it is planned. `TASK-574` and `TASK-573` squash a ticket branch's bookkeeping at landing; this ticket does the same for planning.

Sketch, to settle while planning:

- A planning session works in its own worktree on a branch from `main`, and every `chitty` write there commits to that branch as today.
- Landing: when a ticket is ready for `todo` (or the session ends), squash the branch's commits since its last landing into one commit (for example `chitty: plan TASK-598, TASK-599`), rebase onto `main`, and fast-forward `main`. A tool does these steps, not the agent: probably reuse `git.squash_bookkeeping` from `TASK-574`, since every commit on a planning branch is bookkeeping.
- Until it lands, the runner and other agents do not see the branch's tickets, which is what we want for new tickets. For an existing ticket being re-planned (for example one a worker sent back to `planning`), the copy on `main` stays in `planning`, so the runner cannot pick it up meanwhile.

Open questions:

- How cold readers read the branch's copy: they run `chitty show` from the main checkout today, and `ticket_source` would not find a planning branch (it looks at `main` and `task-<n>` branches).
- What happens when someone else edits the same ticket on `main` meanwhile: the rebase conflicts on the ticket file (`TASK-359` merges two edits of a ticket file).
- The command. The person, 2026-11-22: a command for landing a planning branch is fine, and expected one command for landing any branch, perhaps taking a type. Today no such command exists: the runner lands tickets internally (`_land_locked` in `src/chitty/run.py`), and people land by hand with `git rebase` and `git merge --ff-only`. Planner's suggestion: one `chitty land [BRANCH]` (default the current branch) that works out the kind from the branch, a `task-<n>` branch being landed as the runner does today (rebase, setup, checks, review must have passed) and any other branch being a planning or fix branch (squash bookkeeping commits, rebase, run the checks, fast-forward `main`), so no type option is needed unless a case appears that the name cannot decide.

## History

- 2026-11-16T09:50:22Z intrepid-coral-raven → backlog
- 2026-11-22T22:09:51Z plucky-umber-wren: changed description
- 2026-11-22T22:09:51Z plucky-umber-wren backlog → planning
- 2026-11-22T22:51:30Z plucky-umber-wren: changed dependencies
- 2026-11-22T22:52:42Z plucky-umber-wren: changed description
