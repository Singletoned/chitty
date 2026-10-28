---
title: suggest resolves registered project names before local paths
status: review
created: 2026-10-28
---

## Description

inbox.suggest checks Path(project).is_dir() before registered names. Every Chitty repo has a chitty/ folder, so 'chitty suggest chitty ...' from inside any repo resolves to ./chitty and fails with 'no Chitty configuration in chitty'. A registered name should always win, and the argument should be treated as a path only when it looks like one.

## Acceptance Criteria

- [x] A registered project name wins even when a same-named directory exists in cwd
- [x] The argument is treated as a path only when it contains a '/', is '.', or starts with '~' or '.'
- [x] A bare unregistered name that matches a local directory is an unknown project (with --create advice), not a path
- [x] A regression test running from inside a Chitty repo fails before the fix and passes after; PLAN.md, README and suggest --help describe the rule

## Plan

Inspect project target resolution and its inbox tests, add a regression that reproduces a registered name colliding with a local directory, confirm it fails before the implementation change, then make path recognition explicit, update docs and command help, and run the full check suite.

## Notes

Suggestion origin: circuitry

Decided with the human: path-shaped arguments only; no explicit flag.

Review failed: the fix is correct, but the regression test does not catch the bug in isolation. `suggest` resolves `Path(project)` against the process working directory, not the `cwd` argument, and test_inbox never chdirs. The test only failed before the fix because `make check` runs from the chitty repo root, which happens to have a `chitty/` folder. Checked by running the test against the pre-fix inbox.py from a directory without `chitty/`: it passes. Make the test chdir into self.root (which has `chitty/`) and confirm that it fails against the pre-fix code from any working directory.

Fixed the review finding: the collision regression now runs from inside the temporary Chitty repo, so it reproduces the old path-resolution behavior independently of the repository checkout. Verified with `make check`.

## Summary

Registered project names now take precedence over local directories; only path-shaped arguments are resolved as paths. Added collision, bare-name, and explicit-path coverage; documented the rule in CLI help and README. Confirmed the regression failed before the fix and verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → doing
- 2026-10-28 doing → review
