---
title: Start `chitty run` agents with only the Chitty extension
status: todo
priority: high
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-04
---

## Description

Workers and reviewers are short-lived, one ticket per session, but `chitty run` starts Pi with everything the person has installed: `pi-observational-memory`, `context-mode`, `pi-subagent`, `planning.ts` and more. That spends tokens on memory a throwaway session will never reuse, and adds tools and hooks the ticket did not ask for. A `TASK-132` worker used `pi-subagent` for a cold read that was not its job, and it failed twice.

Have `chitty run` start Pi as `pi --no-extensions -e <agent dir>/extensions/chitty.ts --chitty-<mode> <ID>`. Checked on 2026-11-04: `pi -ne -e ~/.pi/agent/extensions/chitty.ts --help` lists only the two Chitty flags, so this drops discovered extensions and those from `packages` in `settings.json`. Pi keeps its built-in compaction, skills and context files.

Get the path from the helper in `src/chitty/actor.py` that `install_pi_extension` uses, so `PI_CODING_AGENT_DIR` is honoured. Change the call in `src/chitty/run.py` as it stands after `TASK-126`, which forwards extra arguments to Pi. That forwarding is the way to add one back, as in `chitty run -e ./search.ts`, so add no setting.

If the file is missing, fail with a message saying to run `chitty init`, before any claim or worktree, in the `TASK-126` preflight.

Out of scope: `pi` started by hand, which still loads everything; other harnesses; a Chitty setting listing extensions.

## Acceptance Criteria

- [ ] A test with a fake `pi` shows work and review sessions both started with `--no-extensions` and `-e` naming the extension under `PI_CODING_AGENT_DIR`, plus the `--chitty-<mode>` flag and ticket ID
- [ ] A test shows arguments given to `chitty run` still reach `pi` after those flags
- [ ] A test shows a missing extension file failing with a message naming `chitty init`, with no claim and no worktree created
- [ ] `README.md` and `PLAN.md` say which extensions agents get and how to add one, and `README.md` no longer implies `context-mode` runs in `chitty run` sessions
- [ ] A real `chitty run` session is checked to have no `ctx_` or `subagent` tools and no `Observational memory` output, and the result is recorded in a note

## History

- 2026-11-04T09:25:40Z lively-panda → todo
