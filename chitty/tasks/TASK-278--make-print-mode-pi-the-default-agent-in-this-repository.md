---
title: Make print-mode Pi the default agent in this repository
status: review
owner: human
depends_on:
  - TASK-277
parent: TASK-275
created: 2026-11-11
---

## Description

- In the main checkout, set `agent_command` in `chitty.toml` to the `pi-print` command, passing the guide as `{prompt}`. Pi can take it in its system prompt instead, with `--append-system-prompt {prompt}`; that is the command's choice, and Chitty needs no change for it.
- Remove or migrate the extension-based `pi-tui` command in `chitty.toml`, so this repository no longer advertises the retired extension. Then try one work run and one review run, by hand. A config change on `main`, not a ticket branch.

## Notes

Moved to todo by the planner, 2026-11-12: TASK-277 is done.

The default was already print-mode Pi with `{prompt}`. Removed the obsolete `pi-tui` command from `chitty.toml` in commit `c2eae4b`; `make check` passed. Human verification remains: one work run and one review run.

Human, 2026-11-14: one work run and one review run with print-mode Pi completed by hand, as the human reported.

## History

- 2026-11-11T13:21:34Z vivid-yellowhammer → backlog
- 2026-11-11T13:41:51Z vivid-yellowhammer: changed dependencies
- 2026-11-12T18:02:16Z kind-yellow-vole backlog → todo
- 2026-11-12T18:02:17Z kind-yellow-vole: changed notes
- 2026-11-13T22:16:05Z mellow-umber-lapwing: changed description
- 2026-11-13T22:56:25Z mellow-umber-lapwing: changed notes
- 2026-11-13T22:56:25Z mellow-umber-lapwing todo → doing
- 2026-11-14T09:26:09Z jolly-silver-falcon: changed notes
- 2026-11-14T09:26:09Z jolly-silver-falcon doing → review
