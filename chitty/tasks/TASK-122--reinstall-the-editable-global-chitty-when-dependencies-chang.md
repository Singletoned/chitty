---
title: Reinstall the editable global `chitty` when dependencies change
status: todo
created: 2026-11-03
---

## Description

An editable `uv tool` install picks up code from `main` but not new dependencies, so merging a dependency change gives other repositories `ModuleNotFoundError` until the tool is reinstalled. Decide how the reinstall happens, for example a step in the review merge or a clear error naming the command. See `TASK-118`.

## Acceptance Criteria

- [ ] Merging a change to dependencies in `pyproject.toml` cannot silently leave the global `chitty` broken

## History

- 2026-11-03T11:39:03Z eager-raven → todo
