---
title: Print the cold reader's instructions with `chitty guide cold-read`
status: doing
priority: medium
owner: human
created: 2026-11-07
---

## Description

A planner starting a cold read writes the reader's instructions by hand each time: make a detached worktree, run setup with `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` unset, write the tests first and see them fail, implement, run the check, keep the work under `refs/cold-read/<ID>/<n>`, remove the worktree, never write to Chitty, and report findings in a fixed shape. On 2026-11-07 the planner wrote nearly the same long prompt four times for `TASK-63`, `TASK-67` and `TASK-198`. Most of it already sits in `src/chitty/roles/plan.md`, addressed to the planner rather than the reader.

Add a `cold-read` role:

- New file `src/chitty/roles/cold-read.md`, addressed to the reader. It covers both kinds of read in `plan.md`: implementing the ticket in a throwaway worktree when it changes code, and reading the ticket and referenced code when there is nothing to run. It holds the worktree, setup, `refs/cold-read` and cleanup steps, the rule against Chitty writes and changes under `chitty/`, seeing new tests fail first, trying behaviour rather than assuming, and the report: what done means, files changed, open decisions, unverified behaviour, unhandled states and wrong claims, each with file, line, why it matters and the exact wording to change.
- Add `cold-read` to `ROLE_NAMES` in `src/chitty/store.py`, so `chitty guide cold-read` and `chitty guide cold-read <ID>` print it, the latter with the existing `Work only on Chitty ticket <ID>.` line first.
- In `plan.md`, replace the reader's steps with a line telling the planner to start the reader with `chitty guide cold-read <ID>` plus the ticket ID, the code most at risk and what it doubts. The planner's own steps stay: choosing the model, recording outcomes, repeating after a serious finding.
- Mention the role in `PLAN.md`'s cold read section.

No `__version__` bump: role files are package data printed by `chitty guide`, and `chitty init` writes nothing new.

Out of scope: listing `cold-read` in the managed `AGENTS.md` block (`src/chitty/guide.md`), and `chitty next` or `chitty run` starting cold reads.

## Acceptance Criteria

- [ ] A test in `tests/test_guide_cold_read.py` shows `chitty guide cold-read` printing the worktree, `refs/cold-read` and no-Chitty-writes instructions, and `chitty guide cold-read TASK-1` printing them after `Work only on Chitty ticket TASK-1.`
- [ ] A test shows `chitty guide plan` pointing at `chitty guide cold-read` and no longer containing `git update-ref refs/cold-read`
- [ ] `make check` passes

## History

- 2026-11-07T09:37:30Z vivid-dormouse → backlog
- 2026-11-07T09:37:55Z vivid-dormouse backlog → doing
