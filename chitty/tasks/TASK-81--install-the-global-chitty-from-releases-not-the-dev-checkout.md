---
title: Install the global `chitty` from releases, not the dev checkout
status: review
priority: high
depends_on:
  - HUMAN-4
created: 2026-11-01
---

## Description

Both `chitty` commands on this machine are editable installs of this checkout (`~/.local/bin/chitty` from `uv tool` and the repo venv), so every repository runs whatever this working tree contains: a half-finished edit or a branch checkout here changes Chitty for circuitry and the rest. The `uv tool` metadata also still says 0.1.4 while it runs newer code, so `chitty_version` checks in other repos are wrong. Reinstall the global tool from PyPI (with the `mcp` extra) once a release exists; keep the editable install only in this repo's own venv. Document the setup in `README.md`.

## Plan

Inspect the release version and current installation metadata, then replace only the global `uv` tool installation with the released `chitty[mcp]` package while retaining this checkout\u0027s development environment. Document the supported global-versus-development setup in `README.md`, verify the installed version and extras, run `make check`, tick applicable criteria, and run `chitty fix`.

## Notes

Blocked by `TASK-80` and `HUMAN-4`: a release must exist before replacing the global editable installation.

No longer waits on TASK-80 (deferred): it needs only a published release (HUMAN-4).

`HUMAN-4` is done: 0.1.15 is on PyPI (release run `41422338867`).

## Summary

Reinstalled the global `uv` tool from PyPI as `chitty[mcp]==0.1.15`; it now imports from the tool environment rather than this checkout. Documented the released global-install versus repository-local development setup in `README.md`. Verified the global CLI version and MCP entry point, then ran `make check` and `chitty fix`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
- 2026-11-02T10:55:02Z lively-otter blocked → todo
- 2026-11-02T11:00:02Z frosty-falcon todo → doing
- 2026-11-02T11:00:02Z frosty-falcon: wrote the plan
- 2026-11-02T11:01:17Z frosty-falcon doing → review
