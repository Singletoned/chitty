---
title: Run every test without agent environment variables
status: doing
labels:
  - bug
created: 2026-11-11
---

## Description

- `test_guide_backticks` passed in `chitty run`'s pre-agent check and for the planner, but failed inside every print-mode Pi worker, because Pi sets `PI_CODING_AGENT` (fixed in `eb8a01a`). 32 of 52 test files do not use `RepoTestCase`, which already strips such variables, so any of them can behave differently inside an agent.
- In `tests/__init__.py`, which every test run imports first, remove from `os.environ` every variable starting `PI_`, `CLAUDE_`, `CODEX_` or `CHITTY_`, which covers the names `RepoTestCase` excludes; leave `RepoTestCase` as it is. A test that needs one sets it itself. Put the test in `tests/test_agent_environment.py`. Then the pre-agent check, a person, and a worker all see the same result.

## Acceptance Criteria

- [ ] A test in `tests/test_agent_environment.py`, run with `PI_CODING_AGENT=true`, `CLAUDE_CODE_SESSION_ID=x` and `CHITTY_ACTOR=x` exported, finds no variable starting `PI_`, `CLAUDE_`, `CODEX_` or `CHITTY_` in `os.environ`, both in the full run and when run alone. It fails today.
- [ ] `make check` passes with those variables exported.

## Plan

Add a focused unittest in tests/test_agent_environment.py that asserts no PI_, CLAUDE_, CODEX_, or CHITTY_ variables remain. First run it with the specified variables exported to confirm it fails. Then clear those prefixes in tests/__init__.py at import time, rerun the isolated test and full make check with the variables exported, and commit only the two implementation/test paths.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-297/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T21:09:07Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:19Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:18:03Z vivid-yellow-raven: changed description
- 2026-11-11T21:18:04Z vivid-yellow-raven: changed acceptance criteria, notes
- 2026-11-11T21:18:04Z vivid-yellow-raven cold-read → todo
- 2026-11-11T21:54:52Z brisk-ebony-kestrel todo → doing
- 2026-11-11T21:55:14Z brisk-ebony-kestrel: wrote the plan
