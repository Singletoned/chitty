---
title: Retire the Chitty Pi extension
status: todo
labels:
  - needs-minor
depends_on:
  - TASK-320
  - TASK-321
parent: TASK-275
created: 2026-11-11
---

## Description

Remove the bundled Pi extension and its interactive commands, startup flags and usage-file writer without replacements, once `chitty init` no longer installs it. Update current setup guidance, generated examples and documentation to use a `{prompt}` runner command instead of extension flags. Update or remove remaining extension-specific tests, but preserve unrelated Node tooling including Prettier. Do not edit `chitty.toml` on a ticket branch; its local `pi-tui` migration is in `TASK-278`. Historical tickets need not be rewritten. `chitty run` must continue to pass `CHITTY_ACTOR` to descendants: add a fake agent and child process regression without starting a real agent session. No property is needed for fixed documentation text; enumerate changed examples. Write tests first and record failure without the change.

## Acceptance Criteria

- [ ] The bundled extension and its extension-only tests are removed; current generated examples and guidance use `{prompt}` without extension flags. A generated-example regression test fails before the change.
- [ ] A fake `chitty run` agent and its child inherit the same `CHITTY_ACTOR`; demonstrate the test catches removal of runner actor propagation by mutation. `make check` passes.

## Notes

Possible starting point: ticket files at `refs/cold-read/TASK-279/1`, after prerequisites; inspect with `git show refs/cold-read/TASK-279/1:<path>`. Check against the current criteria; do not trust it. The ref includes trial prerequisite commits.

The extension-based repository command was removed in `c2eae4b`; the human trials in `TASK-278` are independent of extension removal.

## History

- 2026-11-11T13:21:35Z vivid-yellowhammer → backlog
- 2026-11-13T22:14:12Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:14:12Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:14:35Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-13T22:14:36Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:16:03Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-13T22:16:03Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:16:06Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:17:01Z mellow-umber-lapwing: changed description
- 2026-11-13T22:17:01Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:17:02Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:19:36Z mellow-umber-lapwing: changed description
- 2026-11-13T22:19:36Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:19:38Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:23:01Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:23:01Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:24:52Z mellow-umber-lapwing: changed dependencies, description, acceptance criteria
- 2026-11-13T22:44:35Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:44:35Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:51:59Z mellow-umber-lapwing: changed notes
- 2026-11-13T22:51:59Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:52:01Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:52:01Z mellow-umber-lapwing planning → todo
- 2026-11-13T23:23:50Z mellow-umber-lapwing: changed dependencies, notes
