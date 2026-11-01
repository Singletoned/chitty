---
title: Release with a single `mate release`
status: backlog
priority: high
created: 2026-11-01
---

## Description

Releasing means bumping `pyproject.toml` by hand in the right change, committing, then tagging and pushing, and in practice it has not happened: PyPI and the last tag are at 0.1.1 while `pyproject.toml` says 0.1.5. Make `mate release` (a `release` Makefile target) do everything. Rule (decided with the human, 2026-11-01): a release that needs `chitty init` re-running is a minor bump, everything else is a patch, unless there's a good reason. The target can find out exactly which applies: run `init` from the last released version in a temporary repo, then `init` from this checkout, and call it minor if the second changes anything. An optional `# args: level` overrides. Versions are then decided at release time, not in each change, so the project rule 'bump `version` in the same change' in `AGENTS.md` goes away.

## Acceptance Criteria

- [ ] `mate release` refuses unless on `main`, with a clean tree, up to date with `origin/main`, and `make check` passing
- [ ] It picks minor or patch relative to the last `v*` tag by comparing `init` output from the last release and from this checkout; `mate release minor` or `mate release patch` overrides
- [ ] It bumps `pyproject.toml` and `uv.lock`, refreshes this repo's `chitty.toml` with `chitty init`, commits `Release vX.Y.Z`, tags `vX.Y.Z`, and pushes `main` and the tag so `release.yml` publishes
- [ ] `AGENTS.md` (project section) and `README.md` describe releasing with `mate release` and drop the per-change version-bump rule; `mate --list` shows the target

## History

- 2026-11-01 → backlog
