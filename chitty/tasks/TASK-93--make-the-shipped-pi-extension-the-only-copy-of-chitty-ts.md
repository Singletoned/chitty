---
title: Make the shipped Pi extension the only copy of `chitty.ts`
status: todo
priority: high
created: 2026-11-01
---

## Description

`~/.pi` is its own Git repo and holds a newer `agent/extensions/chitty.ts`: commit `85bf6c1` ("Stop Chitty continuation after failed turn") adds `continuationAssistantCount`, `stopContinuation` and stopping on `error`/`aborted` turns. None of that is in `src/chitty/integrations/pi/chitty.ts`. `install_pi_extension` overwrites the installed file whenever it differs, so the next `chitty init` in any repo silently discards that work. The shipped copy also reads the TypeScript-private `ctx.sessionManager.sessionId`; it works at runtime only because `private` is compile-time. The installed copy uses the public `getSessionId()`.

## Acceptance Criteria

- [ ] `src/chitty/integrations/pi/chitty.ts` includes the continuation-stop changes from `~/.pi` commit `85bf6c1`, with tests
- [ ] The shipped extension calls `ctx.sessionManager.getSessionId()`
- [ ] `chitty init` does not silently discard local edits to the installed `chitty.ts`; it fails loudly and says how to proceed
- [ ] `README.md` says the shipped file is the source of truth and extension edits belong in this repo

## History

- 2026-11-01 → todo
