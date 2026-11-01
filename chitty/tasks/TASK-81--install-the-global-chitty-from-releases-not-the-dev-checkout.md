---
title: Install the global `chitty` from releases, not the dev checkout
status: blocked
priority: high
depends_on:
  - HUMAN-4
created: 2026-11-01
---

## Description

Both `chitty` commands on this machine are editable installs of this checkout (`~/.local/bin/chitty` from `uv tool` and the repo venv), so every repository runs whatever this working tree contains: a half-finished edit or a branch checkout here changes Chitty for circuitry and the rest. The `uv tool` metadata also still says 0.1.4 while it runs newer code, so `chitty_version` checks in other repos are wrong. Reinstall the global tool from PyPI (with the `mcp` extra) once a release exists; keep the editable install only in this repo's own venv. Document the setup in `README.md`.

## Notes

Blocked by `TASK-80` and `HUMAN-4`: a release must exist before replacing the global editable installation.

No longer waits on TASK-80 (deferred): it needs only a published release (HUMAN-4).

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
