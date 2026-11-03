---
title: "`chitty --version` reports stale package metadata instead of the running code"
status: todo
created: 2026-11-03
---

## Description

`src/chitty/cli.py:52` uses `click.version_option(package_name="chitty")`, which reads `importlib.metadata`. On 2026-11-03 it printed 0.1.17 while `__version__` was 0.1.19. `TASK-83` moved `CHITTY_VERSION` to the code but missed this path. Pass `version=CHITTY_VERSION` and add a regression test.

## History

- 2026-11-03T11:27:23Z eager-raven → todo
