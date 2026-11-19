---
title: Keep `tests/test_guide_backticks.py` independent of this repository's `chitty.toml`
status: cold-read
labels:
  - blocks-release
priority: high
created: 2026-11-19
---

## Description

`test_warning_is_in_every_generated_guide` in `tests/test_guide_backticks.py` runs `chitty guide` with no role in the current directory, which is this checkout, and compares it with `managed_guide("runner")`. So it reads this repository's real `chitty.toml`: when the `0.5.0` release raised `chitty_version`, the workflow resolved to `tickets` and the test failed on `main` and on every branch that merged it, with no code change.

Decisions:

- The no-role case runs in a `RepoTestCase` temporary repository (`tests/support.py`): `os.chdir(self.root)` with the old directory restored by `addCleanup`, as `CliTestCase.setUp` in `tests/test_cli.py` does. For each workflow, `tickets` and `runner`, write the fixture `CONFIG` with its `workflow = "runner"` line set to that workflow, and assert `chitty guide` prints `managed_guide(<workflow>)` and contains the warning. Both managed guides contain it today. The role cases (`work`, `review`, `plan`) are unchanged.
- Other tests: on 2026-11-19 the planner ran the whole unittest suite in a throwaway checkout of `main` with its `chitty.toml` changed (the `workflow` line removed, `chitty_version = "0.6.0"`). Apart from prettier tests (that checkout had no `node_modules`), only this test failed. `tests/test_guide_pi_warning.py` and `tests/test_mcp.py` (near line 235) also read this checkout's config but compare it with itself, so they pass whatever it holds; out of scope.

No property: a fixed set of two workflows, both listed and tested.

## Acceptance Criteria

- [ ] The no-role case runs in the temporary repository, once per workflow (`tickets` and `runner`), and prints `managed_guide(<workflow>)` with the warning
- [ ] Shown by hand and recorded in a note: in the worker's worktree, with `chitty.toml` changed as the Decisions describe (not committed), the test passes after the change and fails before it; `make check` passes with the file restored

## History

- 2026-11-19T10:01:38Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:51Z quick-ginger-lapwing: changed labels
- 2026-11-19T11:22:35Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:22:35Z quick-ginger-lapwing planning → cold-read
