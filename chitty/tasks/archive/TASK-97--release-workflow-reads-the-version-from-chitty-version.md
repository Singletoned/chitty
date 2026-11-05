---
title: Release workflow reads the version from `chitty.__version__`
status: done
priority: high
created: 2026-11-01
---

## Description

`release.yml` checks the tag with `uv version --short`, which fails on dynamic versions: "We cannot get or set dynamic project versions in: pyproject.toml". Since TASK-83 the version lives in `src/chitty/__init__.py` (`[tool.hatch.version]`), so every release fails at that step. Seen in run `41350613045` for `v0.1.13` on 2026-11-01; nothing reached PyPI.

## Acceptance Criteria

- [x] `release.yml` compares the tag with the version the package actually builds with

## Plan

Move the check after `make install` and read `chitty.__version__` with `uv run`; verify the command locally against matching and mismatching tags.

## Notes

Implemented by lively-otter (Claude Code). Ran the new check locally with `GITHUB_REF_NAME=v0.1.13` (passes) and `v0.1.12` (fails); parsed the YAML to confirm the folded command. Not yet run in Actions: `v0.1.13` already points at a commit without this fix, so the next release needs a new version.

Reviewed: inspected commit `01e53f7`; the workflow now imports `chitty.__version__` after dependency installation. Parsed the workflow YAML, verified matching and mismatching tag checks locally, and ran `make check` (183 tests passed).

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
- 2026-11-05T14:44:50Z vivid-wren done → archived
