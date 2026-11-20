---
title: Keep one agent log per `chitty run` ticket run and print its path
status: backlog
priority: high
depends_on:
  - TASK-276
created: 2026-11-19
---

## Description

Follows `TASK-276`, which lets `_run_agent` copy agent output to a log it is given. This ticket gives `chitty run` one log per ticket run. Plan it once `TASK-276` lands, checking these directions against the landed code (cold reads of the combined ticket on 2026-11-19 settled them):

- Pure function `log_path(git_common_dir: Path, ticket_id: TaskId, now: datetime) -> Path` giving `<git common dir>/chitty/run/<ID>-<YYYYMMDDTHHMMSSffffffZ>.log` (UTC, microseconds, zero-padded); test it with fixed timestamps.
- `_run_ticket` (`src/chitty/run.py`) creates the directory (`mkdir(parents=True, exist_ok=True)`) and the file (`open(path, "x", encoding="utf-8")`) as its first change, before the review no-branch `error` edit and the `todo` → `doing` claim, so a failure leaves the ticket unchanged; any `OSError` (`FileExistsError` included, not retried) becomes a `ChittyError` naming the path.
- One log covers every session of the run: `_agent_sessions` (continuations) and `_prepare_review`'s rebase-conflict session; `_run_session` and `_prepare_review` get a required `log: TextIO` parameter and pass it to `_run_agent`.
- `_run_ticket` owns the file: in a `finally` around everything after creating it (setup, review preparation, agent, landing), it closes it and prints `log: <path>` to stderr, so the line appears on every outcome, including failures before the agent starts.
- Tests: a fake agent (pattern in `tests/test_run_continue.py`) printing to both streams and committing a status change; a timeout; a read-only run directory (restore `0o700` with `addCleanup`, and fail, never skip, if a write still succeeds). `chitty run`'s stdout stays exactly its status line.
- Docs: `README.md` and `docs/plan/next-action-and-runner.md` name the `chitty/run/` directory and the `log:` line; a reviewer checks by reading both.

## History

- 2026-11-19T21:23:41Z sunny-white-dormouse → backlog
- 2026-11-19T21:23:43Z sunny-white-dormouse: changed dependencies
- 2026-11-20T08:38:59Z lively-bronze-crane: changed description
