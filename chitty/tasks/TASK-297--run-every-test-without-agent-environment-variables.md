---
title: Run every test without agent environment variables
status: cold-read
labels:
  - bug
created: 2026-11-11
---

## Description

- `test_guide_backticks` passed in `chitty run`'s pre-agent check and for the planner, but failed inside every print-mode Pi worker, because Pi sets `PI_CODING_AGENT` (fixed in `eb8a01a`). 32 of 52 test files do not use `RepoTestCase`, which already strips such variables, so any of them can behave differently inside an agent.
- In `tests/__init__.py`, which every test run imports first, remove from `os.environ` every variable starting `PI_`, `CLAUDE_`, `CODEX_` or `CHITTY_`, which covers the names `RepoTestCase` excludes; leave `RepoTestCase` as it is. A test that needs one sets it itself. Put the test in `tests/test_agent_environment.py`. Then the pre-agent check, a person, and a worker all see the same result.

## Acceptance Criteria

- [ ] A test, run with `PI_CODING_AGENT=true`, `CLAUDE_CODE_SESSION_ID=x` and `CHITTY_ACTOR=x` exported, finds none of them in `os.environ`. It fails today.
- [ ] `make check` passes with those variables exported.

## History

- 2026-11-11T21:09:07Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:19Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:18:03Z vivid-yellow-raven: changed description
