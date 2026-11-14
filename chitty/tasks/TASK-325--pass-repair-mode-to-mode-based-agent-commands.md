---
title: Pass repair mode to mode-based agent commands
status: cold-read
owner: planning
parent: TASK-318
created: 2026-11-13
---

## Description

An error repair is currently selected by `chitty run --errors` but internally treated as `work`; `{prompt}` commands get the repair guide by special case, while `{mode}` commands receive `work` and may start an ordinary worker. Give repair its own `repair` mode when rendering `{mode}` for an error ticket; `{prompt}` commands must continue to receive the repair guide. Ordinary work and review keep their existing modes and guides. Preserve the existing `--errors` selection interface and repair result validation. Update command guidance where it documents supported modes. Use Hypothesis to generate valid command argument lists with `{mode}` and `{id}` and verify substitution preserves other arguments and passes `repair` only for repair; test the `{prompt}` repair path too. Write tests first and record the pre-fix failure. This ticket does not change missing-branch recovery.

## Acceptance Criteria

- [ ] Generated command-rendering tests show error repair renders `{mode}` as `repair` rather than `work`, without changing other arguments; work and review remain unchanged. The repair case fails before the fix.
- [ ] A fake repair agent invoked via `chitty run --errors` receives `repair` in a `{mode} {id}` command; a `{prompt}` command receives the repair guide. Existing repair result validation remains effective.

## History

- 2026-11-13T23:27:52Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:22Z mellow-umber-lapwing: changed description
- 2026-11-14T09:23:14Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-14T09:23:14Z mellow-umber-lapwing backlog → planning
- 2026-11-14T09:23:18Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:23:18Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:27:53Z mellow-umber-lapwing cold-read → planning
- 2026-11-14T09:27:55Z mellow-umber-lapwing planning → cold-read
