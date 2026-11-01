---
title: Give Pi agents a Chitty identity on every command path
status: review
priority: high
created: 2026-11-01
---

## Description

A Pi agent cannot write: Chitty finds `PI_CODING_AGENT=true` but no `PI_SESSION_ID`, even after TASK-75, `chitty init` and a restart.

Diagnosis (2026-11-01, from Pi 1.4.0's code, `dist/core/tools/bash.js`):
- `exposeSessionEnvironment` is not a Pi setting. It is an option of Pi's built-in bash tool, and it defaults to `true`. Nothing reads it from `settings.json`, so the key `chitty init` writes there has no effect.
- Pi deletes `PI_SESSION_ID` from every command's environment and adds it back only inside its own bash tool, when that tool runs with a tool context.
- Every other path loses it: context-mode's `ctx_execute`-style tools (installed here; they run commands in its own server process), extensions calling `pi.exec` (including Chitty's own Pi extension), and anything else that spawns processes. Subagents from `@mjakl/pi-subagent` are new Pi processes, so their bash tool exposes their own session ID: a different name from the parent, against the rule that subagents count as their parent.
- Chitty has no fallback: TASK-75's process-ancestry idea was not implemented.

Proposed fix: Chitty's Pi extension (TASK-87) sets an identity variable in the Pi process's own environment at `session_start`, derived from the session ID. Every child process inherits it: bash, `pi.exec`, servers started afterwards, and subagent Pi processes. So subagents get the parent's name automatically. It must take precedence over `PI_SESSION_ID` so a subagent's own ID does not win. Stop writing `exposeSessionEnvironment` to Pi's settings. Workaround until then: start Pi with `CHITTY_ACTOR=<name>` set.

## Acceptance Criteria

- [x] In a Pi session with Chitty's extension, Chitty resolves the same name from the bash tool, from `pi.exec`, and from a subagent; tests cover the extension setting the variable and Chitty preferring it
- [x] `chitty init` no longer writes `exposeSessionEnvironment` to Pi's settings and removes the key it added earlier; `chitty guide`'s Pi message describes the real requirement
- [x] Commands launched by servers started before `session_start` (such as context-mode) are covered too, or the limitation is documented with the `CHITTY_ACTOR` workaround
- [x] `README.md` and `PLAN.md` describe how Pi identity works

## Plan

Replace the ineffective Pi settings mutation with extension-owned identity propagation. Inspect the actor resolver, shipped extension, guide, README, PLAN, and existing tests; add regression tests that fail under the current behavior, then implement the smallest shared identity mechanism and document the startup-server limitation or workaround. Verify focused tests and `make check`, tick criteria, and submit for independent review.

## Notes

Suggestion origin: chitty

Diagnosed by lively-otter (Claude Code) by reading Pi's installed code, not in a live Pi session; confirm which command path the failing agent used.

Implemented extension-owned `CHITTY_PI_SESSION_ID` propagation, actor precedence, obsolete-settings removal, and the startup-server `CHITTY_ACTOR` workaround documentation. Verified with focused identity tests, `chitty init`, `chitty fix`, `chitty check`, `make check`, and `make test`; existing unrelated Markdown-delimiter warnings remain.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
