---
title: Release a version containing TASK-77
status: blocked
priority: high
created: 2026-11-01
---

## Description

Releasing pushes `main` and a tag and publishes to PyPI, so a person runs it. TASK-81 (install the global `chitty` from releases) needs a release that contains TASK-77. Until `mate release` exists (TASK-80, deferred), release by hand as `AGENTS.md` describes: bump `version` (`pyproject.toml`, or wherever TASK-83 puts it), commit, then push `main` and a tag `v<version>`; `release.yml` checks, builds and publishes.

## Notes

Blocked for a release maintainer: bump the package version, push `main`, and push the release tag so GitHub Actions can publish to PyPI. This agent cannot perform the required release and publishing actions.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → blocked
