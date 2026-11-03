---
title: Do not install the Pi extension from a linked worktree
status: todo
labels:
  - bug
priority: high
created: 2026-11-03
---

## Description

`init_repo` in `src/chitty/store.py` calls `install_pi_extension`, which copies the running code's `src/chitty/integrations/pi/chitty.ts` to `~/.pi/agent/extensions/chitty.ts`. When code on a ticket branch runs `chitty init`, or a write that triggers the setup upgrade, unfinished extension code becomes active for every Pi session on the machine. On 2026-11-03 at 20:21 the `TASK-126` worker did this. The next `chitty run`, still on `main` code, started Pi in the main checkout, and the leaked extension refused to start.

Only install from a main checkout, not a linked Git worktree (`git rev-parse --git-dir` differs from `--git-common-dir`). `chitty init` run outside a Git repository still installs, as now. Report when installation is skipped, so it is not a surprise. Immediate repair was to run `chitty init` from the main checkout.

Out of scope: other setup writes from a worktree, such as `chitty.toml`, which belong to the branch.

## Acceptance Criteria

- [ ] A test with a real `git worktree` and a temporary `PI_CODING_AGENT_DIR` runs `chitty init` in the worktree and shows the installed extension unchanged, and it fails before the fix
- [ ] A test shows `chitty init` in the main checkout still installs and updates the extension
- [ ] A test shows a write that triggers the setup upgrade from a worktree does not install it
- [ ] `PLAN.md` states the rule, and `__version__` is bumped only if setup output changes

## History

- 2026-11-03T20:41:13Z lively-panda → todo
