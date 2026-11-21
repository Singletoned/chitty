---
title: Keep one agent log per `chitty run` ticket run and print its path
status: planning
priority: high
depends_on:
  - TASK-276
created: 2026-11-19
---

## Description

Keep one persistent agent-output file for each selected `chitty run` ticket attempt, shared by work, review or error repair and its continuation/rebase sessions. `TASK-276` landed `_run_agent(log: BinaryIO)`, which merges stdout/stderr, appends by byte offset, and returns only the current session bytes for error reporting. Preserve those semantics, status transitions, timeout handling and stdout. Leave `.chitty/check.log`, usage logging, pruning (`TASK-465`) and error-note changes (`TASK-466`) alone.

In `src/chitty/run.py` add pure `log_path(git_common_dir: Path, ticket_id: TaskId, now: datetime) -> Path`, using the given timezone-aware timestamp converted to UTC, with filename `<ID>-<YYYYMMDDTHHMMSSffffffZ>.log` inside `<git common dir>/chitty/run/`. Format the four-digit year even for years below 1000. Resolve the common directory using `chitty.config.git_common_dir`; if missing, fail with `ChittyError` naming the repository. Use `datetime.now(UTC)` in the caller only.

Scope file ownership to `_run_ticket` (factor a helper or use a context manager). Open before its first ticket status, branch or worktree mutation, including the missing-review-branch error path. `run_next` preflight/housekeeping and no-ticket outcomes are outside this contract. Use `mkdir(parents=True, exist_ok=True)` then `Path.open("x+b")`, never append to an already-existing file. Convert create-time `OSError` to `ChittyError` naming the log path and original error. Once opened, close on every exit and print `log: <absolute path>` to stderr in cleanup, including setup failure, interruption and early return. No `log:` line if creation failed. Pass the same required `BinaryIO` via `_agent_sessions`, `_run_session` and `_prepare_review` to `_run_agent`; remove the per-session `TemporaryFile`. Do not copy setup/check output into this log.

Tests: add `tests/test_run_log.py` using real files and Git. Hypothesis draws `TaskId`s with valid ASCII prefixes and integer or alphanumeric suffixes, safe absolute common directory paths and aware datetimes generated from UTC instants in years 2–9998 with fixed offsets up to ±12 hours, including UTC. Compare result with joining the input path to `chitty/run` and formatting `now.astimezone(UTC)` components explicitly (not the production filename formatter); include a fixed year 9 case. For creation failures use current setup on committed main and an unclaimed todo ticket with a valid fake command. Patch `chitty.run.log_path` to one deterministic file path under the real common dir: either seed that exact file with sentinel bytes, or make its parent a regular file. `run --ticket ID` must exit 1 naming the path, leave the sentinel unchanged, produce no `log:` announcement and leave HEAD, ticket bytes/status and ticket branch/worktree absent or unchanged. This exercises real filesystem errors without permission assumptions.

For success copy the fixture pattern of `tests/test_run_continue.py`: first fake-agent session leaves the ticket doing, next commits review. Emit distinct flushed stdout/stderr markers from both sessions, then assert exactly one log contains all four in session order, with only the existing status line on CLI stdout. Extend the successful conflict fixture in `tests/test_review_rebase_session.py` with distinct markers from the rebase and reviewer commands; assert both are in one new log for the review invocation, in order (separate previous runs from the count). For timeout use the CLI fixture pattern in `tests/test_run_timeout.py` and a flush-before-sleep marker; assert the marker survives in the named log and existing timeout outcome is unchanged. For setup failure use an executable fake agent and committed `setup = "false"`; assert the log is empty, its path is reported and the existing setup error behavior is unchanged. These fixed cases exercise real child processes and runner phases, not a new pure policy. Before fixing, demonstrate the new behavior assertions fail (stub the pure helper for its test if needed), then run the focused tests and `make check`.

## Acceptance Criteria

- [ ] Hypothesis checks the pure log path for generated aware datetimes, IDs and common dirs against the UTC filename recipe. A deterministic collision and a blocked parent path each fail loudly before ticket or ticket branch/worktree changes; neither overwrites existing bytes.
- [ ] A real-Git fake-agent continuation and a rebase-conflict session followed by review each produce one persistent file containing both streams of each session in order. A successful run keeps the exact original status line on stdout and prints exactly one absolute `log:` path on stderr.
- [ ] Timeout and pre-agent setup failure each leave a readable persistent log and print its path exactly once. Document the location and stderr line in `README.md` and `docs/plan/next-action-and-runner.md`. Keep existing timeout, review and continuation tests passing.

## History

- 2026-11-19T21:23:41Z sunny-white-dormouse → backlog
- 2026-11-19T21:23:43Z sunny-white-dormouse: changed dependencies
- 2026-11-20T08:38:59Z lively-bronze-crane: changed description
- 2026-11-21T20:02:04Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T20:02:04Z eager-ginger-adder backlog → cold-read
- 2026-11-21T20:02:56Z eager-ginger-adder cold-read → planning
