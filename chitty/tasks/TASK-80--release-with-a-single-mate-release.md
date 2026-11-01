---
title: Release with a single `mate release`
status: backlog
priority: low
created: 2026-11-01
---

## Description

Releasing means bumping `pyproject.toml` by hand in the right change, committing, then tagging and pushing, and in practice it has not happened: PyPI and the last tag are at 0.1.1 while `pyproject.toml` says 0.1.5. Make `mate release` (a `release` Makefile target) do everything. Rule (decided with the human, 2026-11-01): a release that needs `chitty init` re-running is a minor bump, everything else is a patch, unless there's a good reason. The target can find out exactly which applies: run `init` from the last released version in a temporary repo, then `init` from this checkout, and call it minor if the second changes anything. An optional `# args: level` overrides. Versions are then decided at release time, not in each change, so the project rule 'bump `version` in the same change' in `AGENTS.md` goes away.

## Acceptance Criteria

- [ ] `mate release` refuses unless on `main`, with a clean tree, up to date with `origin/main`, and `make check` passing
- [ ] It bumps `pyproject.toml` and `uv.lock`, refreshes this repo's `chitty.toml` with `chitty init`, commits `Release vX.Y.Z`, tags `vX.Y.Z`, and pushes `main` and the tag so `release.yml` publishes
- [ ] `AGENTS.md` (project section) and `README.md` describe releasing with `mate release` and drop the per-change version-bump rule; `mate --list` shows the target
- [ ] It picks minor or patch relative to the last `v*` tag by comparing `init` output from the last release and from this checkout, ignoring the `chitty_version` line; `mate release minor` or `mate release patch` overrides

## Plan

Inspect the existing Makefile, release workflow, tags, and setup output. Add a guarded `mate release` target that determines the required version bump from setup changes, updates generated files, verifies checks, commits, tags, and pushes. Add hermetic tests for bump selection and guards; update release documentation; run `make check` and target tests before requesting review.

## Notes

Blocked pending HUMAN-6: the specified `init` comparison always changes `chitty_version`, so it cannot distinguish patch from minor. Implementation would encode an unintended always-minor policy.

Unblocked: HUMAN-6 decided that the comparison ignores `chitty_version` (criterion rewritten, now number 4).

Blocked on TASK-83: `chitty init` reads the installed package metadata version, so release automation cannot reliably refresh `chitty.toml` to its newly selected source version. Resolve TASK-83 first; then implement and verify the release command against the corrected version source.

Deferred by the human (2026-11-01): not urgent; a multi-step manual release is fine for now. Dependency on TASK-83 removed to break the cycle; revisit once TASK-83 has fixed where the version lives.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-01 blocked → backlog
