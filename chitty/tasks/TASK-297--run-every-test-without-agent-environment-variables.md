---
title: Run every test without agent environment variables
status: review
labels:
  - bug
created: 2026-11-11
---

## Description

- `test_guide_backticks` passed in `chitty run`'s pre-agent check and for the planner, but failed inside every print-mode Pi worker, because Pi sets `PI_CODING_AGENT` (fixed in `eb8a01a`). 32 of 52 test files do not use `RepoTestCase`, which already strips such variables, so any of them can behave differently inside an agent.
- In `tests/__init__.py`, which every test run imports first, remove from `os.environ` every variable starting `PI_`, `CLAUDE_`, `CODEX_` or `CHITTY_`, which covers the names `RepoTestCase` excludes; leave `RepoTestCase` as it is. A test that needs one sets it itself. Put the test in `tests/test_agent_environment.py`. Then the pre-agent check, a person, and a worker all see the same result.

## Acceptance Criteria

- [x] A test in `tests/test_agent_environment.py`, run with `PI_CODING_AGENT=true`, `CLAUDE_CODE_SESSION_ID=x` and `CHITTY_ACTOR=x` exported, finds no variable starting `PI_`, `CLAUDE_`, `CODEX_` or `CHITTY_` in `os.environ`, both in the full run and when run alone. It fails today.
- [x] `make check` passes with those variables exported.

## Plan

Add a focused unittest in tests/test_agent_environment.py that asserts no PI_, CLAUDE_, CODEX_, or CHITTY_ variables remain. First run it with the specified variables exported to confirm it fails. Then clear those prefixes in tests/__init__.py at import time, rerun the isolated test and full make check with the variables exported, and commit only the two implementation/test paths.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-297/1`. Check it against the current criteria; do not trust it.

Confirmed regression: the isolated test failed before implementation with PI_CODING_AGENT, CLAUDE_CODE_SESSION_ID, and CHITTY_ACTOR exported. After clearing all four prefixes in tests/__init__.py, it passes in isolation with those exports. make check passed Ruff, pyright, and all 502 Python tests. It reached npm test but returned without its normal summary, so the full check remains unverified.

Verified make check with PI_CODING_AGENT=true, CLAUDE_CODE_SESSION_ID=x, and CHITTY_ACTOR=x exported: exit status 0. Ruff, pyright, all 502 Python tests, and npm test completed successfully. The Node dot reporter emits no trailing summary; its exit status is zero.

## Summary

Implemented environment-prefix clearing in tests/__init__.py and added the agent-environment regression test. Verified the regression failed before the fix, passes in isolation, and make check exits 0 with the requested variables exported. Commit: e7e934b (Task: TASK-297). No follow-ups.

## History

- 2026-11-11T21:09:07Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:19Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:18:03Z vivid-yellow-raven: changed description
- 2026-11-11T21:18:04Z vivid-yellow-raven: changed acceptance criteria, notes
- 2026-11-11T21:18:04Z vivid-yellow-raven cold-read → todo
- 2026-11-11T21:54:52Z brisk-ebony-kestrel todo → doing
- 2026-11-11T21:55:14Z brisk-ebony-kestrel: wrote the plan
- 2026-11-11T21:57:59Z brisk-ebony-kestrel: changed notes; ticked acceptance criteria
- 2026-11-11T21:59:04Z brisk-ebony-kestrel: changed notes, summary; ticked acceptance criteria
- 2026-11-11T21:59:04Z brisk-ebony-kestrel doing → review
