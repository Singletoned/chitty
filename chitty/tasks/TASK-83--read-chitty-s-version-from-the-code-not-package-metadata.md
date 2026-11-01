---
title: Read Chitty's version from the code, not package metadata
status: backlog
priority: high
depends_on:
  - TASK-80
created: 2026-11-01
---

## Description

`CHITTY_VERSION` comes from `importlib.metadata`, which an editable install only refreshes on reinstall, so it reported 0.1.4 while running 0.1.5 code and `init` recorded the wrong `chitty_version` in other repos. Keep the version in one place the running code reads directly (for example `src/chitty/__init__.py` as the build's version source), so even an editable install reports correctly. `mate release` bumps that place.

## History

- 2026-11-01 → backlog
