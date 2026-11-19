---
title: Keep `tests/test_guide_backticks.py` independent of this repository's `chitty.toml`
status: planning
labels:
  - blocks-release
priority: high
created: 2026-11-19
---

## Description

`test_warning_is_in_every_generated_guide` in `tests/test_guide_backticks.py` runs `chitty guide` in the current directory, which is this checkout, and compares it with `managed_guide("runner")`. So it reads this repository's real `chitty.toml`: when the `0.5.0` release raised `chitty_version`, the workflow resolved to `tickets` and the test failed on `main` and on every branch that merged it, with no code change. Run the CLI in a `RepoTestCase` temporary repository with a known config instead, and check that no other test reads the real config the same way (for example `git grep -n "Path.cwd()" tests`).

## Acceptance Criteria

- [ ] The test runs `chitty guide` with no arguments in a temporary repository whose config sets `workflow = "runner"`, and passes whatever `workflow` and `chitty_version` this checkout's own `chitty.toml` holds: shown by running it with this checkout's `workflow` line removed and `chitty_version = "9.0.0"`
- [ ] The note lists any other test found reading this checkout's config, each fixed the same way. `make check` passes

## History

- 2026-11-19T10:01:38Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:51Z quick-ginger-lapwing: changed labels
