---
title: Make the shipped Pi extension the only copy of `chitty.ts`
status: doing
priority: high
created: 2026-11-01
---

## Description

`~/.pi` is its own Git repo and holds a newer `agent/extensions/chitty.ts`: commit `85bf6c1` ("Stop Chitty continuation after failed turn") adds `continuationAssistantCount`, `stopContinuation` and stopping on `error`/`aborted` turns. None of that is in `src/chitty/integrations/pi/chitty.ts`. `install_pi_extension` overwrites the installed file whenever it differs, so the next `chitty init` in any repo silently discards that work. The shipped copy also reads the TypeScript-private `ctx.sessionManager.sessionId`; it works at runtime only because `private` is compile-time. The installed copy uses the public `getSessionId()`.

## Acceptance Criteria

- [x] `src/chitty/integrations/pi/chitty.ts` includes the continuation-stop changes from `~/.pi` commit `85bf6c1`, with tests
- [x] The shipped extension calls `ctx.sessionManager.getSessionId()`
- [x] `chitty init` does not silently discard local edits to the installed `chitty.ts`; it fails loudly and says how to proceed
- [x] `README.md` says the shipped file is the source of truth and extension edits belong in this repo

## Plan

1. Compare the installed Pi extension at `~/.pi` commit `85bf6c1` with the shipped integration and port the continuation-stop behavior using the public session ID API.
2. Change installation to reject a locally modified installed extension rather than overwriting it, and add focused tests.
3. Document the source-of-truth policy, run `make format` and `make check`, then tick the verified criteria.

## Notes

Verified with `make format`, `make check`, and `npm test`. The focused regression tests failed before the implementation and pass afterward.

Returning to `doing`: the shipped extension changes existing installations through `chitty init`, so the repository guidance requires a patch version bump before review.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → doing
