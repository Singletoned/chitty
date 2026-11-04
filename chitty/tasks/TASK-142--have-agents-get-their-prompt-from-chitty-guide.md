---
title: Have agents get their prompt from `chitty guide`
status: todo
priority: medium
depends_on:
  - TASK-141
  - TASK-136
parent: TASK-140
created: 2026-11-04
---

## Description

Second of three parts of `TASK-140`. Give every agent its prompt from Chitty, so the prompts stop being tied to Pi.

Change `src/chitty/integrations/pi/chitty.ts` to get its prompt by running `chitty guide <mode> <ID>` at start, and delete `chittyPrompt` and its instruction strings. If that command fails, notify and shut down, as a failing `chitty show` does. The extension and the global `chitty` can differ in version for a while, so an older `chitty` without roles must produce that failure, not an empty prompt.

Add a `{prompt}` placeholder to `agent_command` from `TASK-136`, replaced with the output of `chitty guide <mode> <ID>`. It is replaced after `shlex.split` like the others, so it stays one word whatever it contains, as in `claude "{prompt}"`. `TASK-136` requires both `{mode}` and `{id}`; a command with `{prompt}` is also valid, because the prompt names both.

Out of scope: continuing a stopped agent or any other per-agent integration, which remain `TASK-89` and `TASK-90`; `CHITTY_PI_SESSION_ID`.

## Acceptance Criteria

- [ ] Node tests show the extension sending the output of `chitty guide <mode> <ID>`, and notifying and shutting down when that command fails or prints nothing
- [ ] `chittyPrompt` and its strings are gone from `src/chitty/integrations/pi/chitty.ts`
- [ ] A test with a fake agent shows `{prompt}` arriving as one argument, containing quotes and newlines unchanged, in work and review modes, and a command with `{prompt}` but neither `{mode}` nor `{id}` accepted
- [ ] A real `chitty run` work session is checked to start with the role's instructions, and the result is recorded in a ticket note
- [ ] `README.md` and `PLAN.md` describe `{prompt}`, and `__version__` is bumped above `main`'s

## History

- 2026-11-04T11:56:19Z lively-panda → todo
