---
title: Rebase-conflict agent cannot start when the conflict is in the file its launcher parses
status: backlog
created: 2026-11-23
---

## Description

Observed in echonomicon on 2026-11-22 with TASK-171.

What happened:
1. The review's integration step rebased `task-171` onto `main` and hit a conflict in `pyproject.toml`. TASK-170 had changed the same `extend-select` line.
2. The runner started a rebase-resolution agent in the worktree while the rebase was still in progress. That agent exited with status 2 before doing anything. Log: `.git/chitty/run/TASK-171-20261122163343174193Z.log`.
3. The project's `agent_command` is `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync pi -p ...`. `uv run` parses `pyproject.toml` first, and failed with `TOML parse error at line 52: <<<<<<< HEAD`. So no agent can ever start while that file has conflict markers.
4. The runner moved the ticket back to `doing` and started a work agent in the same worktree, which was still mid-rebase with the markers in place. That agent died the same way (`...163434048700Z.log`), and `chitty run` stopped with exit 1. A stale `TASK-171.lock` was left behind, naming a dead PID.

Fixed by hand: I resolved the conflict (union of both lists), ran `git rebase --continue`, and `mate check` passed.

Suggestions:
- When the rebase agent exits non-zero, run `git rebase --abort` before giving the ticket back. That way later agents start from a clean branch, not a half-finished rebase.
- Try conflict resolution without the agent first. Start the resolution agent in a way that does not depend on parsing the conflicted file.
- Or document that `agent_command` must not depend on files that can conflict, such as `pyproject.toml` through `uv run`. In that case, recommend calling the worktree's `.venv/bin/<agent>` directly, with `PATH` set.
- Report "agent could not start" separately from "agent failed". In this case, the first lines of the log came from `uv`, not the agent.

## Notes

Suggestion origin: echonomicon

Review-path abort now exists (run.py rebase session failure aborts the rebase); the rest is TASK-497, and the could-not-start half is folded into TASK-610.

## History

- 2026-11-23T10:24:23Z witty-russet-gannet → backlog
- 2026-11-23T10:24:24Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:57Z witty-russet-gannet: changed notes
- 2026-11-23T10:28:00Z witty-russet-gannet backlog → archived
