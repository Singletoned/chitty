---
title: Have agents get their prompt from `chitty guide`
status: doing
priority: high
owner: human
depends_on:
  - TASK-141
  - TASK-136
parent: TASK-140
created: 2026-11-04
---

## Description

Second of three parts of `TASK-140`. Give every agent its prompt from Chitty, so the prompts stop being tied to Pi.

Change `src/chitty/integrations/pi/chitty.ts` to get its prompt by running `chitty guide <mode> <ID>` at start, and delete `chittyPrompt` and its instruction strings. If that command fails, notify and shut down, as a failing `chitty show` does. The extension and the global `chitty` can differ in version for a while. Checked on 2026-11-04: `chitty guide work TASK-1` on a `chitty` without roles exits 2 with a usage error, so it takes the failure path. Also checked: plain `chitty guide` works in the `task-126` worktree, where other commands fail because of `TASK-137`, since it loads no configuration; keep it that way. Write this against the `chitty.ts` on `main` after `TASK-126`, which differs from today's.

Add a `{prompt}` placeholder to `agent_command` from `TASK-136`, replaced with what `chitty guide <mode> <ID>` prints, by calling `guide()` directly in `src/chitty/run.py` rather than a subprocess. It is replaced after `shlex.split` like the others, so it stays one word whatever it contains, as in `claude "{prompt}"`. `TASK-136` requires both `{mode}` and `{id}`; a command with `{prompt}` is also valid, because the prompt names both.

Out of scope: continuing a stopped agent or any other per-agent integration, which remain `TASK-89` and `TASK-90`; `CHITTY_PI_SESSION_ID`.

## Acceptance Criteria

- [x] Node tests show the extension sending the output of `chitty guide <mode> <ID>`, and notifying and shutting down when that command fails or prints nothing
- [x] `chittyPrompt` and its strings are gone from `src/chitty/integrations/pi/chitty.ts`
- [x] A test with a fake agent shows `{prompt}` arriving as one argument, containing quotes and newlines unchanged, in work and review modes, and a command with `{prompt}` but neither `{mode}` nor `{id}` accepted
- [ ] A real `chitty run` work session is checked to start with the role's instructions, and the result is recorded in a ticket note
- [x] `README.md` and `PLAN.md` describe `{prompt}`, and `__version__` is bumped above `main`'s

## Plan

Implement prompt retrieval in both agent front ends. The Pi extension will run `chitty guide <mode> <ID>` during startup, send its stdout unchanged, and use the existing startup failure shutdown path for command errors or empty output. The runner will render an optional `{prompt}` placeholder after `shlex.split`, using the in-process `store.guide` function for the selected role and ticket; validation will continue to require `{mode}` and `{id}` unless the command includes the prompt placeholder as specified. Update focused Node/Python tests, README/PLAN documentation, and bump the package patch version. Verify with targeted tests, the full `make check`, and a real `chitty run` work invocation if the local agent setup permits it.

## Notes

Same cold read. Fixed: `{prompt}` calling `guide()` in-process, and an older `chitty` failing, which I ran rather than assumed, as I did `chitty guide` in a worktree. Rejected: a NUL or an over-long prompt, because the text comes from short files we ship. Criterion 4 being a manual check, because no fake can show a real agent receiving the prompt. Colliding version bumps with `TASK-143`, because "above `main`'s" is judged when each is ready for review, and they are ordered by dependency.

Raised to high on 2026-11-04: `TASK-155`, which the human made high priority, needs it.

Real check: ran `chitty run` against the committed implementation. The configured Pi work session started and exited with `TASK-142 was unchanged; only committed changes are visible to chitty run`; no status change was made, so the session did not provide observable evidence of the role instructions beyond the passing fake-agent and extension tests.

Human verification needed for criterion 4: the real `chitty run` invocation launched the configured Pi session but returned unchanged without exposing the initial prompt, so I cannot verify that the visible session began with role instructions. Please run it interactively and confirm the first prompt, then move the ticket to doing and tick criterion 4.

Moved to `doing` by the planning session for the human to check criterion 4 in a real Pi session.

## History

- 2026-11-04T11:56:19Z lively-panda → todo
- 2026-11-04T12:00:38Z lively-panda: changed description, notes
- 2026-11-04T15:38:31Z mellow-newt: changed priority, notes
- 2026-11-05T09:08:52Z upbeat-quail todo → doing
- 2026-11-05T09:09:26Z upbeat-quail: wrote the plan
- 2026-11-05T09:16:59Z upbeat-quail: changed notes
- 2026-11-05T09:17:00Z upbeat-quail: ticked acceptance criteria
- 2026-11-05T09:17:17Z upbeat-quail: changed owner, notes
- 2026-11-05T09:17:17Z upbeat-quail doing → blocked
- 2026-11-05T09:32:19Z mellow-newt: changed notes
- 2026-11-05T09:32:19Z mellow-newt blocked → doing
