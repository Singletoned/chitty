---
title: suggest treats a bare project name as a path when a same-named directory exists
status: backlog
created: 2026-10-28
---

## Description

inbox.suggest checks Path(project).is_dir() before registered project names. Every Chitty repo has a chitty/ task directory, so 'chitty suggest chitty "..."' run from inside any repo resolves to ./chitty (the task folder) and fails with 'Error: no Chitty configuration in chitty'. Expected: a registered project name wins, or paths are only accepted when they contain a separator or start with ~ or ., or the flag is explicit.

## Notes

Suggestion origin: circuitry

## History

- 2026-10-28 → backlog
