---
title: suggest resolves registered project names before local paths
status: todo
created: 2026-10-28
---

## Description

inbox.suggest checks Path(project).is_dir() before registered names. Every Chitty repo has a chitty/ folder, so 'chitty suggest chitty ...' from inside any repo resolves to ./chitty and fails with 'no Chitty configuration in chitty'. A registered name should always win, and the argument should be treated as a path only when it looks like one.

## Acceptance Criteria

- [ ] A registered project name wins even when a same-named directory exists in cwd
- [ ] The argument is treated as a path only when it contains a '/', is '.', or starts with '~' or '.'
- [ ] A bare unregistered name that matches a local directory is an unknown project (with --create advice), not a path
- [ ] A regression test running from inside a Chitty repo fails before the fix and passes after; PLAN.md, README and suggest --help describe the rule

## Notes

Suggestion origin: circuitry

Decided with the human: path-shaped arguments only; no explicit flag.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
